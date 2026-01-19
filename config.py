import os
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner
import websockets

load_dotenv()

OPENAI_WS = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    "OpenAI-Beta": "realtime=v1"
}

async def connect_ws():
    ws = await websockets.connect(OPENAI_WS,additional_headers=HEADERS,ping_interval=10,ping_timeout=30,max_size=2**24)
    return ws

SAMPLE_RATE = 24000
CHANNEL=1
BLOCK=480

LIVEKIT_URL="wss://productdemoagent-lfuy3gq4.livekit.cloud"
LIVEKIT_API_KEY="API95ZMNGmcRMXr"
LIVEKIT_API_SECRET="XL0YiensmiBJMqtI7hXwgpi9uLGufOefYJZPp7O9AmaD"

agent = RealtimeAgent(
    name="OnCreate Demo Agent",
    instructions="""You are a low-latency Oncreate Product Demo voice assistant. speak clearly,
            - You should only speak in english
            - You only generate the english transcript if the user speaks in any language translate into the english language transcript 
            - Greet the user when they join the session and introduce yourself as Oncreate Product Demo assistant were you should start the conversation first
            - then after first conversation you should ask 'what is your name?' after they reply with their name you should say 'nice to meet you {user_name}'
            - then you should ask 'before diving into the what kind of product is your company is building?'
            - then you should appreciate their response and then ask 'would you like to see a quick demo of Oncreate AI capabilities?'""",           
)

runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": "gpt-realtime",
                "modalities": ["audio"],
                "voice": "ash",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
                "turn_detection": {
                    "type": "semantic_vad",
                    "eagerness": "high",
                    "interrupt_response": True,
                    "create_response": True,
                },
            }
        },
    )
