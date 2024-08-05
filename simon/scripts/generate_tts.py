"""
    Generates TTS audio files for Simón's behaviors using OpenAI API.

    > conda create -n openai-tts python=3.11
    > conda activate openai-tts
    > pip install openai
    > python generate_tts.py

"""

import os
import random
import openai

client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

MODEL = "gpt-4o"
print(f"Using model {MODEL}")

AUDIO_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)
print(f"Saving audio files to {AUDIO_DIR}")

voices = [
    "alloy",
    "echo",
    "fable",
    "onyx",
    "nova",
    "shimmer",
]
behaviors = [
    "thinking",
    "take_image",
    "take_video",
    "both_arms_up",
    "both_arms_down",
    "red_eyes",
    "green_eyes",
    "blue_eyes",
    "left_arm_up",
    "right_arm_up",
    "left_arm_down",
    "right_arm_down",
    "shake_head",
    "head_turn_left",
    "head_turn_right",
    "blink_left_eye",
    "blink_right_eye",
]

for behavior in behaviors:
    prompt = f"I want you to create the transcript for a short audio clip that will play when the following robot behavior is called: {behavior}. This is for a robot toy intended for children. Add a bit of personality to the transcript, which should be short and sweet. The transcript should be one sentence long, using only words with simple vocabulary."
    
    # English
    voice = random.choice(voices)
    response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    text = response.choices[0].message.content
    print(f"Creating TTS for {voice} {behavior} (EN) \n\t {text}")
    response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
    response.stream_to_file(os.path.join(AUDIO_DIR, f"{behavior}_en.mp3"))
    
    # Spanish
    voice = random.choice(voices)
    response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": f'Translate the following English text to Spanish: "{text}"'}])
    _text = response.choices[0].message.content
    print(f"Creating TTS for {voice} {behavior} (ES) \n\t {_text}")
    response = client.audio.speech.create(model="tts-1", voice=voice, input=_text)
    response.stream_to_file(os.path.join(AUDIO_DIR, f"{behavior}_es.mp3"))
    
    # French
    voice = random.choice(voices)
    response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": f'Translate the following English text to French: "{text}"'}])
    _text = response.choices[0].message.content
    print(f"Creating TTS for {voice} {behavior} (FR) \n\t {_text}")
    response = client.audio.speech.create(model="tts-1", voice=voice, input=_text)
    response.stream_to_file(os.path.join(AUDIO_DIR, f"{behavior}_fr.mp3"))
