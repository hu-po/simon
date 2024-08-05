import asyncio
from dataclasses import dataclass
import logging
from typing import Dict, List, Union

import gpiozero
from colorzero import Color

from simon.utils import BaseConfig

log = logging.getLogger('gpios')
log.setLevel(logging.INFO)

# GPIO pinout reference
# https://pinout.xyz/

# ---- Miuzei MG90S Servos
# working current: 600mA - 800mA
# operating voltage: 4.8V - 6V
# pulse width range: 500μs - 2500μs
# dead band width: 5μs
# neutral position: 1500μs
# ----

# the servos should be connected to the 4 hardware PWM pins
# https://gpiozero.readthedocs.io/en/stable/api_output.html#angularservo
@dataclass(kw_only=True)
class ServoConfig(BaseConfig):
    pin: int
    pwm: str = "pwm0.a"
    initial_angle: float = 0.0
    min_angle: float = -90.0
    max_angle: float = 90.0
    min_pulse_width: float = 0.0005  # 500µs
    max_pulse_width: float = 0.0025  # 2500µs
    frame_width: float = 0.020  # 20ms (50Hz refresh rate)
    default_move_sleep: float = 0.1 # seconds
    emoji: str = "🦾"

# ---- RGB LED
# RGB LED module with built-in resistors
# common cathode
# voltage: 3.3V - 5V
# current: 20mA
# ----

# the LEDs can be connected to any other GPIO pins
# https://gpiozero.readthedocs.io/en/stable/api_output.html#rgbled
@dataclass(kw_only=True)
class LEDConfig(BaseConfig):
    name: str
    r_pin: int
    g_pin: int
    b_pin: int
    initial_color: str = "purple"
    default_sleep: float = 0.32 # seconds
    emoji: str = "💡"

class GPIO:

    def __init__(self, devices: List[Union[ServoConfig, LEDConfig]]):
        self.config: Dict[str, Union[ServoConfig, LEDConfig]] = {}
        self.servos: Dict[str, gpiozero.AngularServo] = {}
        self.lights: Dict[str, gpiozero.RGBLED] = {}
        devices = devices or []
        for device in devices:
            self.config[device.name] = device
            if isinstance(device, ServoConfig):
                log.info(f"{device.emoji}  servo {device.name} on pin {device.pin}")
                self.servos[device.name] = gpiozero.AngularServo(
                    pin = device.pin,
                    initial_angle=device.initial_angle,
                    min_angle=device.min_angle,
                    max_angle=device.max_angle,
                    min_pulse_width = device.min_pulse_width,
                    max_pulse_width = device.max_pulse_width,
                    frame_width = device.frame_width,
                )
            elif isinstance(device, LEDConfig):
                log.info(f"{device.emoji}  light {device.name} on pins ({device.r_pin}, {device.g_pin}, {device.b_pin})")
                self.lights[device.name] = gpiozero.RGBLED(
                    red=device.r_pin,
                    green=device.g_pin,
                    blue=device.b_pin,
                    active_high=True,
                )
            else:
                log.warning(f"unknown device type: {device}")

    def servos_description(self):
        return f"there are {len(self.servos)} servos: {', '.join(self.servos.keys())}"

    def lights_description(self):
        return f"there are {len(self.lights)} lights: {', '.join(self.lights.keys())}"

    async def async_move_servos(self,
            angles: Union[float, List[float], List[List[float]]] = None,
            servos: Union[str, List[str]] = None,
            sleep: float = None,
        ) -> List[float]:
        servos = servos or self.servos.keys()
        if isinstance(servos, str):
            servos = [servos]
        if isinstance(angles, list):
            if isinstance(angles[0], (float, int)):
                angles = [angles]
        else:
            angles = [[angles]]
        log.info(f"🔩 move servo(s) {servos} to angles(s) {angles}")
        return_angles: List[float] = [self.servos[servo].angle for servo in servos]
        if sleep is not None:
            sleep = sleep / len(angles[0])
        for a in range(len(angles[0])):
            async with asyncio.TaskGroup() as tg:
                for s, servo in enumerate(servos):
                    if a > len(angles[s]):
                        continue # skip for servos with no more angles
                    return_angles[s] = tg.create_task(self.async_set_servo(servo, angles[s][a], sleep))
        return return_angles
    
    async def async_set_servo(self, servo: str, angle: float = None, sleep: float = None) -> float:
        if servo not in self.servos:
            log.warning(f"🔩 servo {servo} not in {self.servos.keys()}")
            return 0
        angle = angle or self.config[servo].initial_angle
        angle = max(self.config[servo].min_angle, min(angle, self.config[servo].max_angle))
        self.servos[servo].angle = angle
        log.debug(f"🔩 set servo {servo} to angle {angle}")
        await asyncio.sleep(sleep or self.config[servo].default_move_sleep)
        return angle

    async def async_set_lights(self,
            colors: Union[str, List[str], List[List[str]]] = None, # list of colors or "blink" or "pulse"
            lights: Union[str, List[str]] = None,
            sleep: float = None,
        ) -> str:
        lights = lights or self.lights.keys()
        if isinstance(lights, str):
            lights = [lights]
        if isinstance(colors, list):
            if isinstance(colors[0], str):
                colors = [colors]
        else:
            colors = [[colors]]
        log.info(f"🔦 set light(s) {lights} to color(s) {colors}")
        return_colors: List[str] = [self.lights[light].color for light in lights]
        if sleep is not None:
            sleep = sleep / len(colors[0])
        for c in range(len(colors[0])):
            async with asyncio.TaskGroup() as tg:
                for l, light in enumerate(lights):
                    if c > len(colors[l]):
                        continue # skip for lights with no more colors
                    color = colors[l][c]
                    if color == "blink":
                        tg.create_task(self.async_light_blink(light, sleep))
                    elif color == "pulse":
                        tg.create_task(self.async_light_blink(light, sleep))
                    else:
                        try:
                            return_colors[l] = color
                            self.lights[light].color = Color(color)
                            await asyncio.sleep(sleep or self.config[light].default_sleep)
                        except Exception as e:
                            log.warning(f"🔦 error setting light {light} to color {color}: {e}")
        return return_colors
    
    async def async_light_pulse(self, light: str, sleep: float = None):
        try:
            sleep = sleep or self.config[light].default_sleep
            assert light in self.lights, f"🔦 light {light} not in {self.lights.keys()}"
            self.lights[light].pulse(
                fade_in_time=sleep / 2.0,
                fade_out_time=sleep / 2.0,
                on_color=self.lights[light].color,
                off_color=(0, 0, 0),
                n=2, # number of times to pulse
                background=True, # return immediately, run in background thread
            )
        except Exception as e:
            log.warning(f"Error pulsing light {light}: {e}")
        finally:
            await asyncio.sleep(sleep)
            # return to previous color when done blinking
            self.lights[light].color = self.lights[light].color
    
    async def async_light_blink(self, light: str, sleep: float = None):
        try:
            sleep = sleep or self.config[light].default_sleep
            assert light in self.lights, f"🔦 light {light} not in {self.lights.keys()}"
            self.lights[light].blink(
                on_time=sleep / 2.0,
                off_time=sleep / 2.0,
                fade_in_time=0, 
                fade_out_time=0, 
                on_color=self.lights[light].color,
                off_color=(0, 0, 0),
                n=2, # number of times to blink
                background=True, # return immediately, run in background thread
            )
        except Exception as e:
            log.warning(f"Error blinking light {light}: {e}")
        finally:
            await asyncio.sleep(sleep)
            # return to previous color when done blinking
            self.lights[light].color = self.lights[light].color
    
    def __del__(self):
        for servo in self.servos.values():
            servo.close()
        for light in self.lights.values():
            light.close()
        log.info("terminated GPIO controller")