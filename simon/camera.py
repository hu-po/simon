from dataclasses import dataclass
import asyncio
import logging
import os
import subprocess

from simon import IMAGE_DIR
from simon.utils import BaseConfig

log = logging.getLogger('camera')
log.setLevel(logging.INFO)

@dataclass(kw_only=True)
class CameraConfig(BaseConfig):
    name: str
    emoji: str = "📸"
    device_id: int = 0
    # image
    default_image_name: str = "_🖼️📸_"
    image_filetype: str = "png"
    image_width: int = 640
    image_height: int = 480
    rpicam_timeout: float = 0.6
    # video
    default_video_name: str = "_🖼️🎥_"
    video_filetype: str = "mp4"
    video_width: int = 640
    video_height: int = 480
    video_duration: float = 1.0
    video_framerate: int = 30
    # timeouts for async operations
    max_retries: int = 11
    retry_delay: float = 0.01

class Camera:

    def __init__(self, config: CameraConfig = None):
        self.config: CameraConfig = config or CameraConfig(name="picam")
        self.default_image_path = os.path.join(IMAGE_DIR, f"{self.config.default_image_name}.{self.config.image_filetype}")
        self.default_video_path = os.path.join(IMAGE_DIR, f"{self.config.default_video_name}.{self.config.video_filetype}")
        self.p: subprocess.Popen = None
        self.image_cmd: str = [
            "rpicam-still", 
            "--width", 
            str(self.config.image_width), 
            "--height", 
            str(self.config.image_height),
            "--encoding",
            str(self.config.image_filetype),
            "--timeout",
            str(self.config.rpicam_timeout * 1000),
        ]
        self.video_cmd: str = [
            "rpicam-vid", 
            "--width",
            str(self.config.video_width), 
            "--height", 
            str(self.config.video_height),
            "--framerate",
            str(self.config.video_framerate),
        ]
        log.info(f"{self.config.emoji} started")

    async def async_use_camera(self, name: str = None, duration: float = None) -> str:
        is_video = duration is not None
        name = name or (self.default_video_path if is_video else self.default_image_path)
        filetype = self.config.video_filetype if is_video else self.config.image_filetype
        if not name.endswith(filetype):
            name = f"{name}.{filetype}"
            if not name.startswith(IMAGE_DIR):
                name = os.path.join(IMAGE_DIR, name)
        log_msg = f"new {'video' if is_video else 'image'}"
        log_msg += f" ({duration}s)" if is_video else ""
        log.info(f"{self.config.emoji} {log_msg} [{name}]")
        cmd = (self.video_cmd + ["-o", name, "-t", str(int(duration * 1000))]) if is_video else (self.image_cmd + ["--output", name])
        log.debug(f"{self.config.emoji} {'video' if is_video else 'image'} cmd \n {' '.join(cmd)}")
        is_debug: bool = log.getEffectiveLevel() == logging.DEBUG
        try:
            self.p = await asyncio.create_subprocess_exec(*cmd, stdin=asyncio.subprocess.PIPE if not is_debug else None, stdout=asyncio.subprocess.PIPE if not is_debug else None, stderr=asyncio.subprocess.PIPE if not is_debug else None)
            await asyncio.sleep(duration if is_video else self.config.rpicam_timeout)
            for retry in range(self.config.max_retries):
                if self.p.returncode is not None:
                    log.debug(f"{self.config.emoji} Process finished normally")
                    break
                wait_time = self.config.retry_delay * (2 ** retry)
                log.debug(f"{self.config.emoji} Waiting for process to finish, retry {retry+1}/{self.config.max_retries}, waiting {wait_time}s")
                try:
                    await asyncio.wait_for(self.p.wait(), timeout=wait_time)
                    break
                except asyncio.TimeoutError:
                    if retry == self.config.max_retries - 1:
                        log.warning(f"{self.config.emoji} Process did not finish after max retries, terminating.")
                        self.p.terminate()
                        await self.p.wait()
        except Exception as e:
            log.error(f"{self.config.emoji} Error during {'video' if is_video else 'image'} capture: {e}")
            if self.p:
                self.p.terminate()
                await self.p.wait()
            raise
        return name

    def __del__(self):
        if self.p is not None:
            self.p.terminate()
        log.info(f"{self.config.emoji} terminated")