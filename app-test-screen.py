import gradio as gr

import simon

c = simon.init(['screen'])

with gr.Blocks(theme=c['theme']) as demo:
    gr.Markdown("# Screen Test")
demo.launch()