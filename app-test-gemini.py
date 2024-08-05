import asyncio
from functools import partial
import logging
import os

import gradio as gr

import simon

log = logging.getLogger('test-gemini')
log.setLevel(logging.INFO)

c = simon.init(['audio', 'camera', 'gemini', 'screen'])

# ---- TOOLS 🛠️ ----

def shaka_sign() -> str:
    """Does the shaka sign.
    
    Returns:
        str shaka sign emoji
    """
    return '🤙'

# tools can be async or not
async def thumbs_up() -> str:
    """Does the thumbs up.
    
    Returns:
        str thumbs up emoji
    """
    return '👍'

# ---- TOOLS 🛠️ ----

TOOLS = {
    'shaka_sign': shaka_sign,
    'thumbs_up': thumbs_up,
}

async def use_tool_from_image(image_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('thinking', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_image(image_path))
    return await c['gemini'].async_use_tool(TOOLS, result.result())

async def use_tool_from_audio(audio_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('thinking', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_audio(audio_path))
    return await c['gemini'].async_use_tool(TOOLS, result.result())

async def use_tool_from_video(video_path: str) -> str:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(c['audio'].async_play_audio('thinking', multilingual=True))
        result = tg.create_task(c['gemini'].async_process_video(video_path))
    return await c['gemini'].async_use_tool(TOOLS, result.result())

with gr.Blocks(theme=c['theme']) as demo:
    gr.Markdown("# Gemini Test")
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
                button.click(lambda n=image_path: asyncio.run(c['camera'].async_use_camera(n)), outputs=[image])
                button = gr.Button("🎥 take video")
                button.click(lambda t, n=video_path: asyncio.run(c['camera'].async_use_camera(n, t)), inputs=[slider], outputs=[video])
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
            model_dropdown = gr.Dropdown(
                label="model",
                choices=["models/gemini-1.5-flash-latest", "models/gemini-1.5-pro-latest"],
                value="models/gemini-1.5-flash-latest",
            )
            model_info_text = gr.Textbox(label="model info")
            model_dropdown.change(c['gemini'].change_model, inputs=[model_dropdown], outputs=[model_info_text])
            with gr.Row():
                button_image =  gr.Button("process image")
                button_audio =  gr.Button("process audio")
                button_video =  gr.Button("process video")
            output = gr.Textbox(label="model response")
            button_image.click(partial(use_tool_from_image, image_path=image_path), outputs=[output])
            button_audio.click(partial(use_tool_from_audio, audio_path=audio_path), outputs=[output])
            button_video.click(partial(use_tool_from_video, video_path=video_path), outputs=[output])
demo.queue()
demo.launch()