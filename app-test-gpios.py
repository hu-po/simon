import asyncio

import gradio as gr

import simon

c = simon.init(['gpios', 'screen'])

with gr.Blocks(theme=c['theme']) as demo:
    gr.Markdown("# GPIO Test")
    with gr.Row():
        with gr.Column():
            gr.Markdown(c['gpios'].servos_description())
            for servo in c['gpios'].servos.keys():
                config = c['gpios'].config[servo]
                angle_slider = gr.Slider(config.min_angle, config.max_angle, config.initial_angle, label=servo)
                sleep_slider = gr.Slider(0, 5, config.default_move_sleep, label=f"{servo} sleep")
                angle_slider.change(lambda x, t, s=servo: asyncio.run(c['gpios'].async_move_servos(x, s, t)), inputs=[angle_slider, sleep_slider])
                sleep_slider.change(lambda x, t, s=servo: asyncio.run(c['gpios'].async_move_servos(x, s, t)), inputs=[angle_slider, sleep_slider])
                button = gr.Button("🤸🏼‍♀️  wiggle")
                button.click(lambda t, s=servo, config=config: asyncio.run(c['gpios'].async_move_servos([
                    config.initial_angle,
                    config.min_angle,
                    config.max_angle,
                    config.initial_angle,
                ], s, t)), inputs=[sleep_slider])
        with gr.Column():
            gr.Markdown(c['gpios'].lights_description())
            for light in c['gpios'].lights.keys():
                config = c['gpios'].config[light]
                sleep_slider = gr.Slider(0, 5, config.default_sleep, label=f"{light} sleep")
                with gr.Row():
                    color_picker = gr.ColorPicker(config.initial_color, label=light)
                    color_picker.change(lambda x, t, l=light: asyncio.run(c['gpios'].async_set_lights(x, l, t)), inputs=[color_picker, sleep_slider])
                    sleep_slider.change(lambda x, t, l=light: asyncio.run(c['gpios'].async_set_lights(x, l, t)), inputs=[color_picker, sleep_slider])
                    pulse_button = gr.Button("pulse")
                    pulse_button.click(lambda t, l=light: asyncio.run(c['gpios'].async_set_lights("pulse", l, t)), inputs=[sleep_slider])
                    blink_button = gr.Button("blink")
                    blink_button.click(lambda t, l=light: asyncio.run(c['gpios'].async_set_lights("blink", l, t)), inputs=[sleep_slider])
demo.queue(max_size=3)
demo.launch()