import asyncio
import os
import time
import io
from PIL import Image
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from livekit import rtc, api, agents
from livekit.agents import (
    AgentSession, 
    Agent, 
    room_io,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, noise_cancellation
from config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL
import logging

load_dotenv()

# Configuration

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Conversation state
conversation_state = {
    "stage": "greeting",
    "user_name": None,
    "company_product": None,
    "demo_started": False,
}
ONCREATE_URL="http://agent.oncreate.ai/app.html"

def detect_demo_intent(text: str) -> bool:
    """Detect if user wants to see the demo"""
    positive_keywords = ["yes", "sure", "yeah", "okay", "ok", "show me", "demo", "let's go", "please"]
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in positive_keywords)


class DemoAgent(Agent):
    """Custom agent for OnCreate product demos"""
    
    def __init__(self) -> None:
        self.base_instructions = """You are OnCreate's AI Demo Agent - a helpful, friendly voice assistant.

                                            Core Rules:
                                            - Speak clearly and naturally in English only
                                            - Keep responses concise (1-3 sentences)
                                            - Be warm and conversational
                                            - Listen carefully to understand user needs
                                            - After going inside the demo your going demonstration how to create new ai agent and its features so 
                                              you should say what is exactly in the user_text and you not the extra words.

                                            Conversation Flow:
                                            1. Greet user warmly and ask their name
                                            2. After asking the name you should ask about their company's product
                                            3. After asking the product and you should ask them whether show demo or not
                                            
                                            Remember: You're here to help and showcase OnCreate's power!"""
        
        # Store instructions internally so we can update them later
        self._instructions = self.base_instructions
        super().__init__(instructions=self._instructions)

    @property
    def instructions(self) -> str:
        """Return the agent's current instructions."""
        return self._instructions

    @instructions.setter
    def instructions(self, value: str) -> None:
        """Allow updating instructions from external code."""
        self._instructions = value
    
    def get_current_instructions(self,stage) -> str:
        """Get context-aware instructions based on conversation stage"""
        # stage = conversation_state["stage"]
        
        if stage == "greeting":
            return self.base_instructions + "\n\nIntroduce yourself as Oncreate's demo agent and ask: 'What's your name?'"
        
        elif stage == "asking_name":
            name = conversation_state.get("user_name", "there")
            return self.base_instructions + f"\n\nUser's name is {name}. Say 'Nice to meet you, {name}!' Then ask: 'What kind of product is your company building?'"
        
        elif stage == "asking_company":
            product = conversation_state.get("company_product", "their product")
            return self.base_instructions + f"\n\nUser is building: {product}. Show interest. Then ask: 'Would you like to see a quick demo of OnCreate's AI capabilities?'"
        
        elif stage == "offering_demo":
            return self.base_instructions + "\n\nUser agreed! Say: 'Excellent! Let me show you what OnCreate can do. Watch the screen.'"
        
        elif stage == "demo":
            return self.base_instructions + "\n\nNarrate the demo steps clearly. you should only say what is in the usertext .dont add extra words  :{user_text}."
        
        return self.base_instructions


async def publish_screen_share_lk(room: rtc.Room, page):
    """Capture Playwright screenshots and publish to LiveKit"""
    
    # await asyncio.sleep(1)
    
    # Get dimensions
    png = await page.screenshot(type='png', timeout=60000)
    img = Image.open(io.BytesIO(png)).convert('RGB')
    width, height = img.size
    
    print(f"📺 Screen: {width}x{height}")
    
    # Create video source
    video_src = rtc.VideoSource(width, height)
    local_track = rtc.LocalVideoTrack.create_video_track("screen-share", video_src)
    
    # Publish track
    await room.local_participant.publish_track(
        local_track,
        rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_SCREENSHARE,
            video_encoding=rtc.VideoEncoding(
                max_bitrate=3_000_000,
                max_framerate=15.0,
            )
        )
    )
    
    print("✅ Screen share started")
    
    # Capture loop
    fps = 15
    frame_interval = 1.0 / fps
    
    try:
        while True:
            start_time = time.time()
            
            png = await page.screenshot(type='png', timeout=60000)
            img = Image.open(io.BytesIO(png)).convert('RGB')
            
            if img.size != (width, height):
                img = img.resize((width, height), Image.BILINEAR)
            
            buf = img.tobytes()
            vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)
            timestamp_us = int(time.time() * 1_000_000)
            video_src.capture_frame(vf, timestamp_us=timestamp_us)

            
            
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, frame_interval - elapsed))
            
    except asyncio.CancelledError:
        print("🛑 Screen capture stopped")

    except Exception as ex:
        logging.error(f"Screen Capture Error:{ex}")