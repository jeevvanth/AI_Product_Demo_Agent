import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.io.wavfile import write
import platform
import os
import base64
import json
import websockets
from config import OPENAI_WS,HEADERS

SAMPLE_RATE = 16000

def record_audio(seconds=5, filename="input.wav"):
    print(" Listening...")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(" Recording complete")
    return filename


#TTS Generation

def play_audio(file="response.mp3"):
    """
    Plays audio directly via system audio output using sounddevice.
    Does NOT invoke OS music players.
    """
    data, samplerate = sf.read(file, dtype='float32')

    # Handle mono/stereo automatically
    sd.play(data, samplerate)
    sd.wait()

#WS realtime listening

def pcm16_base64(audio: np.ndarray) -> str:
    # print("Listening...")
    pcm = (audio * 32767).astype(np.int16).tobytes()
    # print("Recorded")
    return base64.b64encode(pcm).decode()

#WS realtime speaking 

async def speak(ws, text):
    
    await ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["audio"],
            "instructions": text,
            "voice": "ash"
        }
    }))
