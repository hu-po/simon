import asyncio
import os

import gradio as gr

import simon

c = simon.init(['audio', 'screen'])

with gr.Blocks(theme=c['theme']) as demo:
    gr.Markdown("# Audio Test")
    gr.Markdown(c['audio'].audio_description())
    with gr.Row():
        with gr.Column():
            for sound in c['audio'].sounds.keys():
                button = gr.Button(sound)
                button.click(lambda s=sound: asyncio.run(c['audio'].async_play_audio(s)))
                button = gr.Button(f"{sound} multilingual")
                button.click(lambda s=sound: asyncio.run(c['audio'].async_play_audio(s, multilingual=True)))
        with gr.Column():
            audio_path = os.path.join(simon.AUDIO_DIR, f'test.{c["audio"].config.filetype}')
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
demo.launch()
