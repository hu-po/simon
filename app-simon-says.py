import asyncio
from functools import partial
import logging
import os

import gradio as gr

import simon

log = logging.getLogger('simon-says')
log.setLevel(logging.INFO)

c = simon.init(['audio', 'camera', 'gemini', 'gpios', 'screen'])

# ---- TOOLS 🛠️ ----

async def both_arms_up() -> str:
    emoji = "🙌"
    log.debug(f"{emoji} both_arms_up")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('both_arms_up', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[-30], [30]], ['arm.left', 'arm.right']))
    return emoji

async def both_arms_down() -> str:
    emoji = "👇"
    log.debug(f"{emoji} both_arms_down")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('both_arms_down', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[40], [-40]], ['arm.left', 'arm.right']))
    return emoji

async def red_eyes() -> str:
    emoji = "👀🔴"
    log.debug(f"{emoji} red_eyes")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('red_eyes', multilingual=True))
        tg.create_task(c['gpios'].async_set_lights([['red'], ['red']], ['eye.left', 'eye.right']))
    return emoji

async def green_eyes() -> str:
    emoji = "👀🟢"
    log.debug(f"{emoji} green_eyes")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('green_eyes', multilingual=True))
        tg.create_task(c['gpios'].async_set_lights([['green'], ['green']], ['eye.left', 'eye.right']))
    return emoji

async def blue_eyes() -> str:
    emoji = "👀🔵"
    log.debug(f"{emoji} blue_eyes")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('blue_eyes', multilingual=True))
        tg.create_task(c['gpios'].async_set_lights([['blue'], ['blue']], ['eye.left', 'eye.right']))
    return emoji

async def left_arm_up() -> str:
    emoji = "👈"
    log.debug(f"{emoji} left_arm_up")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('left_arm_up', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[-30], [-40]], ['arm.left', 'arm.right']))
    return emoji

async def right_arm_up() -> str:
    emoji = "👉"
    log.debug(f"{emoji} right_arm_up")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('right_arm_up', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[40], [30]], ['arm.left', 'arm.right']))
    return emoji

async def left_arm_down() -> str:
    emoji = "👇"
    log.debug(f"{emoji} left_arm_down")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('left_arm_down', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[40], [30]], ['arm.left', 'arm.right']))
    return emoji

async def right_arm_down() -> str:
    emoji = "👇"
    log.debug(f"{emoji} right_arm_down")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('right_arm_down', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([[-30], [-40]], ['arm.left', 'arm.right']))
    return emoji

async def shake_head() -> str:
    emoji = "🤦"
    log.debug(f"{emoji} shake_head")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('shake_head', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([-30, 30, -30, 30, 0], 'head.yaw', 4))
        tg.create_task(c['gpios'].async_set_lights([['red', 'blink', 'blue', 'blink'], ['blink', 'red', 'blink', 'blue']], ['eye.left', 'eye.right'], 3))
    return emoji

async def head_turn_left() -> str:
    emoji = "⬅️"
    log.debug(f"{emoji} head_turn_left")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('head_turn_left', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([30], 'head.yaw'))
    return emoji

async def head_turn_right() -> str:
    emoji = "➡️"
    log.debug(f"{emoji} head_turn_right")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('head_turn_right', multilingual=True))
        tg.create_task(c['gpios'].async_move_servos([-30], 'head.yaw'))
    return emoji

async def blink_left_eye() -> str:
    emoji = "👁️"
    log.debug(f"{emoji} blink_left_eye")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('blink_left_eye', multilingual=True))
        tg.create_task(c['gpios'].async_set_lights(['blink'], ['eye.left']))
    return emoji

async def blink_right_eye() -> str:
    emoji = "👁️"
    log.debug(f"{emoji} blink_right_eye")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('blink_right_eye', multilingual=True))
        tg.create_task(c['gpios'].async_set_lights(['blink'], ['eye.right']))
    return emoji

# ---- TOOLS 🛠️ ----

TOOLS = {
    "both_arms_up": both_arms_up,
    "both_arms_down": both_arms_down,
    "red_eyes": red_eyes,
    "green_eyes": green_eyes,
    "blue_eyes": blue_eyes,
    "left_arm_up": left_arm_up,
    "right_arm_up": right_arm_up,
    "left_arm_down": left_arm_down,
    "right_arm_down": right_arm_down,
    "shake_head": shake_head,
    "head_turn_left": head_turn_left,
    "head_turn_right": head_turn_right,
    "blink_left_eye": blink_left_eye,
    "blink_right_eye": blink_right_eye,
}

async def simon_says_from_image(image_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('think', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_image(image_path, "if there is a human in the image, what pose are they in? what are the left arm and right arm doing? which way is the head facing?"))
    log.debug(f"image.result(): {result.result()}")
    return await c['gemini'].async_use_tool(TOOLS, result.result())

async def simon_says_from_audio(audio_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('think', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_audio(audio_path, "based on this audio clip, how should we raise or lower our left arm and right arm? what direction should we turn our head? should we change our eye color or blink a specific eye? this audio may be in english, espanol, or francais."))
    log.debug(f"audio.result(): {result.result()}")
    return await c['gemini'].async_use_tool(TOOLS, result.result())

async def simon_says_from_video(video_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('think', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_video(video_path, "what are the people in this video doing? how should we move our arms and head to mimic them?"))
    log.debug(f"video.result(): {result.result()}")
    return await c['gemini'].async_use_tool(TOOLS, result.result())

with gr.Blocks(theme=c['theme']) as demo:
    with gr.Row():
        with gr.Column():
            with gr.Row():
                image_path = os.path.join(simon.IMAGE_DIR, f'test_gemini.{c["camera"].config.image_filetype}')
                video_path = os.path.join(simon.IMAGE_DIR, f'test_gemini.{c["camera"].config.video_filetype}')
                audio_path = os.path.join(simon.AUDIO_DIR, f'test_gemini.{c["audio"].config.filetype}')
                image = gr.Image(
                        value=image_path,
                        sources=None,
                        image_mode='RGB',
                        type='filepath',
                        format=c['camera'].config.image_filetype,
                        width=c['screen'].config.visual_component_width,
                        height=c['screen'].config.visual_component_height,
                        show_label=False,
                        show_download_button=False,
                    )
                video = gr.Video(
                    value=video_path,
                    sources=None,
                    show_download_button=True,
                    show_label=False,
                    format=c['camera'].config.video_filetype,
                    width=c['screen'].config.visual_component_width,
                    height=c['screen'].config.visual_component_height,
                )
            slider = gr.Slider(0.0, 10.0, 4.0, label="🎥 video duration")
            with gr.Row():
                button = gr.Button("📸 take image")
                # button.click(lambda n=image_path: asyncio.run(c['camera'].async_use_camera(n)), outputs=[image])
                button.click(
                    lambda n=image_path: asyncio.run(c['camera'].async_use_camera(n)),
                    outputs=[image],
                ).then(partial(simon_says_from_image, image_path=image_path))
                button = gr.Button("🎥 take video")
                # button.click(lambda t, n=video_path: asyncio.run(c['camera'].async_use_camera(n, t)), inputs=[slider], outputs=[video])
                button.click(
                    lambda t, n=video_path: asyncio.run(c['camera'].async_use_camera(n, t)),
                    inputs=[slider],
                    outputs=[video],
                ).then(partial(simon_says_from_video, video_path=video_path))
            with gr.Row():
                record_button = gr.Button("🎙️  record")
                play_button = gr.Button("🔊  play")
            slider = gr.Slider(0.0, 10.0, 4.0, label="🎙️ audio duration")
            audio = gr.Audio(
                value=audio_path,
                sources=None,
                show_download_button=True,
                show_label=False,
                type='filepath',
                format=c['audio'].config.filetype,
            )
            record_button.click(lambda d, n=audio_path: asyncio.run(c['audio'].async_record_audio(n, d)), inputs=[slider], outputs=[audio])
            play_button.click(lambda n: asyncio.run(c['audio'].async_play_audio(n)), inputs=[audio])
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    gr.Markdown("# Simón Says")
                    button_image = gr.Button("from image 📸", variant="primary")
                    button_audio = gr.Button("from audio 🎙️", variant="primary")
                    button_video = gr.Button("from video 🎥", variant="primary")
                with gr.Row():
                    gr.Markdown("# Output")
                    textbox = gr.Textbox(show_label=False, placeholder="hola! hello! bonjour!")
            with gr.Row():
                gr.Image(
                    value=os.path.join(os.path.abspath(os.path.dirname(__file__)), "docs", "thumbnail.png"),
                    sources=None,
                    image_mode='RGB',
                    type='filepath',
                    format=c['camera'].config.image_filetype,
                    width=224,
                    height=224,
                    show_label=False,
                    show_download_button=False,
                )
            button_image.click(partial(simon_says_from_image, image_path=image_path), outputs=[textbox])
            button_audio.click(partial(simon_says_from_audio, audio_path=audio_path), outputs=[textbox])
            button_video.click(partial(simon_says_from_video, video_path=video_path), outputs=[textbox])

demo.queue()
demo.launch()