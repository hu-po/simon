import asyncio
import os

import gradio as gr

import simon

c = simon.init(['camera', 'screen'])

with gr.Blocks(theme=c['theme']) as demo:
    gr.Markdown("# Camera Test")
    with gr.Column():
        with gr.Row():
            image_path = os.path.join(simon.IMAGE_DIR, f'test.{c["camera"].config.image_filetype}')
            video_path = os.path.join(simon.IMAGE_DIR, f'test.{c["camera"].config.video_filetype}')
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
        slider = gr.Slider(0.0, 10.0, 4.0, label="video duration")
        with gr.Row():
            button = gr.Button("📸 take image")
            button.click(lambda n=image_path: asyncio.run(c['camera'].async_use_camera(n)), outputs=[image])
            button = gr.Button("🎥 take video")
            button.click(lambda t, n=video_path: asyncio.run(c['camera'].async_use_camera(n, t)), inputs=[slider], outputs=[video])
demo.launch()