import argparse
import os
import logging
from typing import Any, Dict, List

_this_dir: str = os.path.abspath(os.path.dirname(__file__))
AUDIO_DIR: str = os.path.join(_this_dir, 'audio')
IMAGE_DIR: str = os.path.join(_this_dir, 'image')
# create audio and image directories if they don't exist
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def init(modules: List[str]) -> Dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="enable debug logging", action="store_true")
    name: str = os.getlogin()
    parser.add_argument("--name", type=str, help="config setting", default=name)
    parsed_args = parser.parse_args()
    log = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('|%(relativeCreated)d|%(message)s'))
    if parsed_args.debug:
        log.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
        log.debug("🐛🪲🪳 debug logging enabled 🐛🪲🪳")
        from simon.utils import timer, async_timer
    else:
        log.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
        log.addHandler(handler)
    log.info("🧦 Simón 🎶 🧦")
    log.info("🇺🇸 hello 🍔 \t 🇪🇸 hola 🥘 \t 🇫🇷 bonjour 🥖")
    log.debug(f"name {name}")
    log.debug(f"🗃️ Audio dir: {AUDIO_DIR}")
    log.debug(f"🗃️ Image dir: {IMAGE_DIR}")
    # main state of program is just a dict with singletons for optional modules
    c: Dict[str, Any] = {}
    if 'audio' in modules:
        try:
            log.debug('🗃️ importing audio')
            from simon.audio import Audio

            logging.getLogger('audio').setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)
            logging.getLogger('audio').addHandler(handler)

            if parsed_args.debug:
                Audio.async_play_audio = async_timer(Audio.async_play_audio, 'audio')
                Audio.async_record_audio = async_timer(Audio.async_record_audio, 'audio')
            c['audio'] = Audio()
        except ImportError as e:
            log.error(f"failed to import audio: {str(e)}")
    if 'camera' in modules:
        try:
            log.debug('🗃️ importing camera')
            from simon.camera import Camera

            logging.getLogger('camera').setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)
            logging.getLogger('camera').addHandler(handler)

            if parsed_args.debug:
                Camera.__init__ = timer(Camera.__init__, 'camera')
                Camera.async_use_camera = async_timer(Camera.async_use_camera, 'camera')
            c['camera'] = Camera()
        except ImportError as e:
            log.error(f"failed to import camera: {str(e)}")

    if 'gemini' in modules:
        try:
            log.debug('🗃️ importing gemini')
            from simon.gemini import Gemini

            logging.getLogger('gemini').setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)
            logging.getLogger('gemini').addHandler(handler)

            if parsed_args.debug:
                Gemini.async_file_api = async_timer(Gemini.async_file_api, 'gemini')
                Gemini.async_process_audio = async_timer(Gemini.async_process_audio, 'gemini')
                Gemini.async_process_video = async_timer(Gemini.async_process_video, 'gemini')
                Gemini.async_process_image = async_timer(Gemini.async_process_image, 'gemini')
                Gemini.async_use_tool = async_timer(Gemini.async_use_tool, 'gemini')
                Gemini.change_model = timer(Gemini.change_model, 'gemini')
            c['gemini'] = Gemini()
        except ImportError as e:
            log.error(f"failed to import gemini: {str(e)}")

    if 'gpios' in modules:
        try:
            log.debug('🗃️ importing gpios')
            from simon.gpios import GPIO, ServoConfig, LEDConfig

            logging.getLogger('gpios').setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)
            logging.getLogger('gpios').addHandler(handler)

            if parsed_args.debug:
                GPIO.async_move_servos = async_timer(GPIO.async_move_servos, 'gpios')
                GPIO.async_set_servo = async_timer(GPIO.async_set_servo, 'gpios')
                GPIO.async_set_lights = async_timer(GPIO.async_set_lights, 'gpios')
                GPIO.async_light_pulse = async_timer(GPIO.async_light_pulse, 'gpios')
                GPIO.async_light_blink = async_timer(GPIO.async_light_blink, 'gpios')

            if name=='simon':
                c['gpios'] = GPIO([
                    ServoConfig(name="head.yaw", pwm="pwm1.a", pin=13, min_angle=-30, max_angle=30), # negative to the right
                    ServoConfig(name="arm.left", pwm="pwm0.a", pin=12, min_angle=-45, max_angle=60), # negative up
                    ServoConfig(name="arm.right", pwm="pwm1.b", pin=19, min_angle=-60, max_angle=45), # positive up
                    LEDConfig(name="eye.left", r_pin=23, g_pin=24, b_pin=25),
                    LEDConfig(name="eye.right", r_pin=10, g_pin=9, b_pin=11),
                ])
            elif name=='pi5':
                c['gpios'] = GPIO([
                    ServoConfig(name="head.yaw", pwm="pwm1.a", pin=13), # 0 forward
                    ServoConfig(name="arm.left", pwm="pwm0.a", pin=12), # 90 down, -90 up
                    ServoConfig(name="arm.right", pwm="pwm1.b", pin=19), # -90 down, 90 up
                    # ServoConfig(name="", pwm="pwm0.b", pin=18),
                    LEDConfig(name="eye.left", r_pin=10, g_pin=9, b_pin=11),
                    LEDConfig(name="eye.right", r_pin=23, g_pin=24, b_pin=25),
                    # LEDConfig("light.c", 5, 6, 26),                           
                ])
            elif name=='pi4':
                 c['gpios'] = GPIO([
                    ServoConfig(name="pwm0.a", pin=12),
                    ServoConfig(name="pwm0.b", pin=18),
                    ServoConfig(name="pwm1.a", pin=13),
                    ServoConfig(name="pwm1.b", pin=19),
                    LEDConfig(name="light.a", r_pin=25, g_pin=24, b_pin=23),
                    LEDConfig(name="light.b", r_pin=10, g_pin=9, b_pin=11),
                    # LEDConfig("light.c", 5, 6, 26),
                ])
            else:
                log.warning(f"no gpio devices config found for {name}, set the config in simon/__init__.py")
                c['gpios'] = GPIO()

        except ImportError as e:
            log.error(f"failed to import gpios: {str(e)}")

    if 'screen' in modules:
        try:
            log.debug('🗃️ importing screen')
            from simon.screen import Screen, ScreenConfig

            logging.getLogger('screen').setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)
            logging.getLogger('screen').addHandler(handler)

            config = ScreenConfig(name=name)
            if name=='simon':
                # raspberry pi use chromium
                config.browser_cmd = 'chromium-browser'
                config.close_all_browsers = True
            else:
                log.warning(f"no screen config found for {name}, set the config in simon/__init__.py")
                config.browser_cmd = 'google-chrome'

            c['screen'] = Screen(config)
            GRADIO_THEME: str = 'gstaff/sketch'
            log.debug(f"🎨 GRADIO_THEME: {GRADIO_THEME}")
            c['theme'] = GRADIO_THEME
        except ImportError as e:
            log.error(f"failed to import screen: {str(e)}")

    return c