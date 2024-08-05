from dataclasses import dataclass
import asyncio
import logging
import os
import random
import subprocess
from typing import Dict, Tuple

import pygame as audio_pygame

from simon import AUDIO_DIR
from simon.utils import BaseConfig


log = logging.getLogger('audio')
log.setLevel(logging.INFO)

# ---- Audio
# uses usb speaker and pygame audio mixer
# to play .mp3 files in the assets/audio directory 
# ----

@dataclass(kw_only=True)
class AudioConfig(BaseConfig):
    name: str
    emoji: str = "🔊"
    default_audio_name: str = "user_audio"
    filetype: str = "mp3"
    default_audio_duration_play: float = 3.0
    default_audio_duration_record: float = 6.0
    async_audio_timeout: float = 6.0
    multilingual_choices: Tuple[str] = ("en", "es", "fr")


class Audio:

    def __init__(self, config: AudioConfig = None):
        self.config: AudioConfig = config or AudioConfig(name="pygame")
        self.default_audio_path = os.path.join(AUDIO_DIR, f"{self.config.default_audio_name}.{self.config.filetype}")
        self.sounds: Dict[str, str] = {}
        for root, _, files in os.walk(AUDIO_DIR):
            for file_name in files:
                if file_name.lower().endswith(self.config.filetype):
                    file_path = os.path.join(root, file_name)
                    if os.path.exists(file_path):
                        file_name = file_name.split('.')[0] # remove file extension
                        if file_name.endswith('_es') or file_name.endswith('_fr'):
                            continue # skip, only keep track of _en files
                        log.debug(f"{self.config.emoji} sound [{file_name}] at {file_path}")
                        self.sounds[file_name] = file_path
        # recording is done with arecord
        self.p: subprocess.Popen = None
        self.record_cmd: str = ["arecord"]
        self.start()

    def start(self):
        log.info(f"{self.config.emoji} started")
        audio_pygame.mixer.init()

    def audio_description(self):
        return f"there are {len(self.sounds)} sounds: {', '.join(self.sounds.keys())}"

    async def async_play_audio(self, name: str = None, duration: float = None, multilingual: bool = False) -> str:
        """plays state['audio'] sound file with state['audio'] limited duration using async

        Args:
            name (str): name of audio file
            duration (float): max duration in seconds
            multilingual (bool): if True, play audio a randomly chosen language!
        """
        name = name or self.default_audio_path
        duration = duration or self.config.default_audio_duration_play
        if not name.endswith(self.config.filetype):
            log.info(f"{self.config.emoji} playing sound [{name}]")
            if multilingual:
                name = name[:-3] # remove language modifier
                name = f"{name}_{random.choice(self.config.multilingual_choices)}"
            name = f"{name}.{self.config.filetype}"
            if not name.startswith(AUDIO_DIR):
                name = os.path.join(AUDIO_DIR, name)
        else:
            log.info(f"{self.config.emoji} playing sound at filepath [{name}]")
        try:
            audio_pygame.mixer.music.load(name)
            audio_pygame.mixer.music.play()

            end_time = asyncio.get_event_loop().time() + duration if duration > 0 else float('inf')
            while audio_pygame.mixer.music.get_busy() and asyncio.get_event_loop().time() < end_time:
                await asyncio.sleep(0.1)

            if audio_pygame.mixer.music.get_busy():
                audio_pygame.mixer.music.stop()
                log.debug(f"{self.config.emoji} stopped audio after {duration} seconds")

        except Exception as e:
            log.error(f"{self.config.emoji} error playing {name}: {str(e)}")
        return name

    async def async_record_audio(self, name: str = None, duration: float = None) -> str:
        name = name or self.default_audio_path
        duration = duration or self.config.default_audio_duration_record
        if not name.endswith(self.config.filetype):
            name = f"{name}.{self.config.filetype}"
            if not name.startswith(AUDIO_DIR):
                name = os.path.join(AUDIO_DIR, name)
        log.info(f"{self.config.emoji} new audio [{name}]")
        cmd = self.record_cmd + ["-d", str(int(duration)), name]
        log.debug(f"record cmd \n {' '.join(cmd)}")
        is_debug: bool = log.getEffectiveLevel() == logging.DEBUG
        self.p = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if not is_debug else None,
            stdout=asyncio.subprocess.PIPE if not is_debug else None,
            stderr=asyncio.subprocess.PIPE if not is_debug else None,
        )
        try:
            await asyncio.wait_for(self.p.wait(), timeout=duration + self.config.async_audio_timeout)
        except asyncio.TimeoutError:
            log.error(f"{self.config.emoji} audio recording timed out [{name}]")
            self.p.terminate()
        return name

    def __del__(self):
        audio_pygame.mixer.quit()
        log.info(f"{self.config.emoji} terminated")