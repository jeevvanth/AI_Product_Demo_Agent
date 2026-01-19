import asyncio
import websockets
import json
import os
import base64
import pyaudio
from dotenv import load_dotenv
from config import OPENAI_WS
# Configuration
# OPENAI_WS = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class RealtimeTTS:
    def __init__(self, voice="ash"):
        """
        Initialize TTS client
        voice options: alloy, echo, shimmer, ash, ballad, coral, sage, verse
        """
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.sample_rate = 24000
        self.voice = voice
        self.audio_buffer = []
        self.is_speaking = False
        
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        self.ws = await websockets.connect(
            OPENAI_WS,
            additional_headers=headers,
            ping_interval=20,
            ping_timeout=30,
            max_size=2**24
        )
        
        # Configure session for TTS only
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],  # Must include both
                "instructions": "You are a text-to-speech system. The text are not questions so dont answer to it. Just read the text exactly as given were your an text to speech.dont add any other words.",
                "voice": self.voice,
                "output_audio_format": "pcm16",
                "turn_detection": None,  # Disable turn detection for TTS
                "temperature": 0.6
            }
        }
        await self.ws.send(json.dumps(config))
        
        # Initialize audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=4096
        )
        
    async def speak(self, text):
        """Convert text to speech and play audio"""
        if not self.ws:
            raise Exception("Not connected. Call connect() first.")
        
        self.is_speaking = True
        self.audio_buffer = []
        
        # Create conversation item with the text
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        await self.ws.send(json.dumps(message))
        
        # Request audio response
        response_create = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],  # Must include both
                "instructions": f"Read exactly as written as given in text, the text are not question so dont answer to it please say what is extactly in the text your an tts. dont add extra words while saying: '{text}'"
            }
        }
        await self.ws.send(json.dumps(response_create))
        
        # Wait for audio to complete
        await self._wait_for_audio()
        
    async def _wait_for_audio(self):
        """Listen for audio chunks and play them"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                event_type = data.get("type")
                
                if event_type == "response.audio.delta":
                    # print("going to play the audio")
                    # Receive and play audio chunk
                    audio_b64 = data.get("delta")
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        self.stream.write(audio_bytes)
                        
                elif event_type == "response.audio.done":
                    # Audio generation complete
                    self.is_speaking = False
                    break
                    
                elif event_type == "error":
                    print(f"Error: {data.get('error')}")
                    self.is_speaking = False
                    break
                    
        except Exception as e:
            print(f"Error receiving audio: {e}")
            self.is_speaking = False
            
    async def close(self):
        """Close connection and cleanup"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        if self.ws:
            await self.ws.close()