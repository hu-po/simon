from dataclasses import dataclass
import logging
import os
import subprocess

from simon.utils import BaseConfig

log = logging.getLogger('screen')
log.setLevel(logging.INFO)

@dataclass(kw_only=True)
class ScreenConfig(BaseConfig):
    name: str
    addr: str = "localhost"
    port: str = "7860"
    browser_cmd: str = "chromium-browser"
    close_all_browsers: bool = False
    display_number: str = "0.0"
    # screen size
    width: int = 1920
    height: int = 1080
    # image/video component default sizes
    visual_component_width: int = 224
    visual_component_height: int = 224
    emoji: str = "📱"

class Screen:

    def __init__(self, config: ScreenConfig = None):
        self.config: ScreenConfig = config or ScreenConfig(name="browser")
        self.p: subprocess.Popen = None
        self.browser_cmd: str = self.config.browser_cmd
        os.environ['DISPLAY'] = f":{self.config.display_number}"
        self.cmd: str = [
            self.browser_cmd,
            "--kiosk", # fullscreen
            "--disable-gpu",
            "--use-gl=egl",
            f"http://{self.config.addr}:{self.config.port}",
        ]
        log.debug(f"{self.config.emoji} screen cmd \n {self.cmd}")
        if config.close_all_browsers:
            self.clear()
        self.start()

    def start(self):
        log.info(f"{self.config.emoji} started")
        is_debug: bool = log.getEffectiveLevel() == logging.DEBUG
        self.p = subprocess.Popen(
            self.cmd,
            stdin = subprocess.PIPE if not is_debug else None,
            stdout = subprocess.PIPE if not is_debug else None,
            stderr = subprocess.PIPE if not is_debug else None,
        )
    
    def clear(self):

        log.debug(f"{self.config.emoji} removing any stale browsers")
        os.system(f"killall {self.browser_cmd}")

    def __del__(self):
        if self.p is not None:
            self.p.terminate()
        if self.config.close_all_browsers:
            self.clear()
        log.info(f"{self.config.emoji} terminated")