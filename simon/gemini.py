import asyncio
from dataclasses import dataclass
import inspect
import logging
import os
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import google.generativeai as genai
from google.generativeai.types import file_types

from simon.utils import BaseConfig

log = logging.getLogger('gemini')
log.setLevel(logging.INFO)

@dataclass(kw_only=True)
class GeminiConfig(BaseConfig):
    name: str
    default_model: str = "models/gemini-1.5-pro-latest"
    default_audio_prompt: str = "transcribe this audio, it may be in english, espanol, or francais. provide the translation in english."
    default_image_prompt: str = "describe this image in a short sentence. focus on what the people are doing."
    default_video_prompt: str = "describe this video in a short sentence. focus on what the people are doing."
    default_tool_system: str = "You are a function calling bot. Choose the best function based on a description of multimodal user input."
    emoji: str = "🪐"
    file_api_max_retries: int = 8
    file_api_retry_delay: float = 0.01

class Gemini:

    def __init__(self, config: GeminiConfig = None):
        self.config: GeminiConfig = config or GeminiConfig(name="gemini")
        if 'GOOGLE_API_KEY' not in os.environ:
            log.warning("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
        self.change_model(self.config.default_model)
        log.info(f"{self.config.emoji} started")

    def change_model(self, model_name: str) -> str:
        log.info(f"{self.config.emoji} using model {model_name}")
        model_info = genai.get_model(model_name)
        log.debug(model_info)
        self.model_name = model_name
        return str(model_info)

    async def async_file_api(
        self,
        file_path: str,
        display_name: Optional[str] = None,
        max_retries: int = None,
        retry_delay: float = None,
        ) -> file_types.File:
        max_retries = max_retries or self.config.file_api_max_retries
        retry_delay = retry_delay or self.config.file_api_retry_delay
        try:
            assert os.path.exists(file_path), f"file not found: {file_path}"
            display_name = display_name or file_path
            file = genai.upload_file(path=file_path, display_name=display_name)
            log.debug(f"💾 uploading file {file.display_name} to {file.uri}")
            for retry in range(max_retries):
                if file.state == genai.protos.File.State.ACTIVE:
                    break
                elif file.state == genai.protos.File.State.FAILED:
                    raise ValueError(f"file processing failed: {file.state.name}")
                elif file.state == genai.protos.File.State.PROCESSING:
                    log.debug(f"💾 waiting on file processing, retry {retry+1} of {max_retries}")
                    await asyncio.sleep(retry_delay * 2 ** retry) # exponential backoff
            log.debug(f"💾 file uploaded {display_name}")
            return file
        except Exception as e:
            log.warning(f"💾 error with file_api: {str(e)}")
            return None

    async def async_process_audio(self, audio_path: str, prompt: str = None, model_name: str = None) -> str:
        prompt = prompt or self.config.default_audio_prompt
        model_name = model_name or self.model_name
        log.info("🎙️ audio")
        log.debug(f"🎙️\n\tmodel={model_name}\n\tprompt={prompt}")
        model = genai.GenerativeModel(model_name=model_name)
        audio = await self.async_file_api(audio_path)
        response = await model.generate_content_async([audio, prompt])
        log.debug(f"🎙️ response={response}")
        return response.text

    async def async_process_image(self, image_path: str, prompt: str = None, model_name: str = None) -> str:
        prompt = prompt or self.config.default_image_prompt
        model_name = model_name or self.model_name
        log.info("📷 image")
        log.debug(f"📷\n\tmodel={model_name}\n\tprompt={prompt}")
        model = genai.GenerativeModel(model_name=model_name)
        image = await self.async_file_api(image_path)
        response = await model.generate_content_async([image, prompt])
        log.debug(f"📷 response={response}")
        return response.text

    async def async_process_video(self, video_path: str, prompt: str = None, model_name: str = None) -> str:
        prompt = prompt or self.config.default_video_prompt
        model_name = model_name or self.model_name
        log.info("📹 video")
        log.debug(f"📹\n\tmodel={model_name}\n\tprompt={prompt}")
        model = genai.GenerativeModel(model_name=model_name)
        video = await self.async_file_api(video_path)
        response = await model.generate_content_async([video, prompt])
        log.debug(f"📹 response={response}")
        return response.text
    
    async def async_use_tool(self, tools: Dict[str, Union[Callable, Awaitable]], prompt: str, system: str = None, model_name: str = None) -> str:
        model_name = model_name or self.model_name
        system = system or self.config.default_tool_system
        log.info("🧰 tool")
        log.debug(f"🧰\n\tmodel={model_name}\n\tsystem={system}\n\tprompt={prompt}")
        model = genai.GenerativeModel(
            model_name=model_name,
            tools=tools.values(),
            system_instruction=system,
            # https://ai.google.dev/gemini-api/docs/function-calling#function_calling_mode
            tool_config={"function_calling_config": {
                "mode": "ANY",
                "allowed_function_names": tools.keys(),
            }},
        )
        chat = model.start_chat()
        response = await chat.send_message_async(prompt)
        log.debug(f"🧰 response={response}")
        tool_output = "❓"
        for part in response.parts:
            if fn := part.function_call:
                args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                log.debug(f"🧰 calling {fn.name}({args})")
                if fn.name in tools:
                    if inspect.iscoroutinefunction(tools[fn.name]):
                        tool_output = await tools[fn.name](**fn.args)
                    else:
                        tool_output = tools[fn.name](**fn.args)
                else:
                    log.warning(f"🧰 unknown tool: {fn.name}")
        return tool_output