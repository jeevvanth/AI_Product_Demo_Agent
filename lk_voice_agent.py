
import asyncio
import os
import time
import io
import logging
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
    AgentServer
)
from livekit.plugins import openai, noise_cancellation
from config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL
from meet_interface import start_server,ROOM_NAME,session_lock,active_sessions,random,user_join_queue
from cursor import inject_cursor_styles, set_cursor_mode, click_with_cursor
from run_demo import run
from openai.types import realtime
from livekit.plugins.openai.realtime import RealtimeModel
from helper import is_demo_intent

load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Suppress verbose PIL debug messages
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)
logging.getLogger('PIL.Image').setLevel(logging.WARNING)

# Configuration


# Conversation state
conversation_state = {
    "stage": "greeting",
    "user_name": None,
    "company_product": None,
    "demo_started": False,
    "waiting_for_user": True,
    "last_user_message": None,
}
ONCREATE_URL="http://agent.oncreate.ai/app.html"

def detect_demo_intent(text: str) -> bool:
    """Detect if user wants to see the demo"""
    positive_keywords = ["yes", "sure", "yeah", "okay", "ok", "show me", "demo", "let's go", "please"]
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in positive_keywords)

def extract_name(text: str) -> str:
    """Extract name from user response"""
    # Simple extraction - you can enhance this
    text = text.strip()
    # Remove common phrases
    for phrase in ["my name is", "i'm", "i am", "call me", "it's", "it is"]:
        text = text.lower().replace(phrase, "").strip()
    
    # Take first word as name (capitalize it)
    words = text.split()
    if words:
        return words[0].capitalize()
    return "there"


class DemoAgent(Agent):
    """Custom agent for OnCreate product demos"""
    
    def __init__(self) -> None:
        self.base_instructions = """You are OnCreate's AI Demo Agent - a helpful, friendly voice assistant.

                                            Core Rules:
                                            - Speak clearly and naturally in English only
                                            - Keep responses concise (1-3 sentences)
                                            - Be warm and conversational
                                            - Listen carefully to understand user needs

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
        # if stage == "greeting":
        #     return self.base_instructions + "\n\nGreet warmly: 'Hi! I'm OnCreate's AI assistant. What's your name?'"
        
        # elif stage == "asking_name":
        #     return self.base_instructions + "\n\nWait for the user to provide their name. Listen carefully."
        
        # elif stage == "got_name":
        #     name = conversation_state.get("user_name", "there")
        #     return self.base_instructions + f"\n\nRespond warmly: 'Nice to meet you, {name}! What kind of product is your company building?'"
        
        # elif stage == "asking_company":
        #     return self.base_instructions + "\n\nWait for the user to describe their company's product. Listen carefully."
        
        # elif stage == "got_company":
        #     product = conversation_state.get("company_product", "their product")
        #     return self.base_instructions + f"\n\nShow interest in '{product}'. Then ask: 'Would you like to see a quick demo of OnCreate's AI capabilities?'"
        
        # elif stage == "offering_demo":
        #     return self.base_instructions + "\n\nWait for user to respond yes or no to the demo offer."
        
        # elif stage == "starting_demo":
        #     return self.base_instructions + "\n\nSay enthusiastically: 'Excellent! Let me show you what OnCreate can do. Watch the screen!'"
        
        # elif stage == "demo":
        #     return self.base_instructions + "\n\nThe demo is running. Narrate what's happening on screen if needed."
        
        # return self.base_instructions


async def publish_screen_share(room: rtc.Room, page):
    """Capture Playwright screenshots and publish to LiveKit"""
    
    await asyncio.sleep(1)
    
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
    frame_count = 0
    
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

            # frame_count += 1
            # if frame_count % (fps * 5) == 0:
            #     logger.info(f"📊 Published {frame_count} frames")
            
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, frame_interval - elapsed))


            
    except asyncio.CancelledError:
        print("🛑 Screen capture stopped")

    except Exception as e: 
        logger.error(f"Screen capture error: {e}")



server = AgentServer()



@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit agent"""
    
    print(f"🎤 Starting agent in room: {ctx.room.name}")
    
    # Connect to room
    await ctx.connect()
    print("✅ Connected to LiveKit")

    await start_server()

    
    print("⏳ Waiting for user to submit email...")
    user_info = await user_join_queue.get()
    
    session_id = user_info['session_id']
    user_email = user_info['email']
    
    # Wait for the ready event (triggered when user submits email)
    print(f"✅ User {user_email} joined! Starting initialization for session {session_id}...")
    print("User joined, proceeding with agent...")
    
    playwright = None
    browser = None
    room_obj = None
    
    # Launch Playwright
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        slow_mo=4000,
        args=[
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-sandbox',
        ]
    )
    context = await browser.new_context()
    page = await context.new_page()
    
    print("🌐 Navigating to demo page...")
    await page.goto(ONCREATE_URL, wait_until="domcontentloaded")

    await inject_cursor_styles(page)
    await set_cursor_mode(page, mode="pointer")
    await click_with_cursor(page, 'button[data-title="Agents"]')
    
    print("🔌 Connecting to LiveKit room...")
    room_obj = rtc.Room()
    
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity("Demo-Agent")
    token.with_name("Demo Agent")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=ROOM_NAME,
        can_publish=True,
        can_subscribe=True,
    ))
    jwt_token = token.to_jwt()
    
    await room_obj.connect(LIVEKIT_URL, jwt_token)
    print("✅ Connected to LiveKit room")
    
    screen_task = asyncio.create_task(publish_screen_share(room_obj, page))
    
    # Create agent
    agent = DemoAgent()

    model=RealtimeModel(
        voice="ash",
        modalities=["text","audio"],
        input_audio_transcription=realtime.AudioTranscription(
            model="gpt-4o-transcribe"
        ),
        input_audio_noise_reduction="near_field",
        turn_detection=realtime.realtime_audio_input_turn_detection.SemanticVad(
            type="semantic_vad",
            create_response=True,
            eagerness="auto",
            interrupt_response=True,
        ),
        )

    session= AgentSession(llm=model)
    
    print("🤖 Starting session...")

    
    # Print transcripts to console as they arrive.
    # `.on()` requires a synchronous callback; schedule async work with create_task.
    async def _print_transcript_async(ev):
        try:
            txt = getattr(ev, "transcript", "") or ""
            is_final = getattr(ev, "is_final", False)
            tag = "(final)" if is_final else ""
            logger.info(f"📝 Transcript User: {txt}")

            if detect_demo_intent(txt) or is_demo_intent(txt):
                logger.info("Starting the demo")
                asyncio.create_task(run(page=page, browser=browser, session=session))

            # Example async work you might want to run per-transcript:
            # await some_async_function(ev)
        except Exception:
            logger.exception("error printing transcript")

    def _print_transcript(ev):
        try:
            asyncio.create_task(_print_transcript_async(ev))
        except Exception:
            logger.exception("failed scheduling transcript task")

    session.on("user_input_transcribed", _print_transcript)
    
    
    
    
    # Start session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                    else noise_cancellation.BVC(),
            )
        ),
    )
    
    print("✅ Agent ready")
    

    
    # Monitor conversation
    async def monitor_conversation():

        # import pdb; pdb.set_trace()
        
        last_stage = conversation_state["stage"]
        logger.info("Starting conversation monitor")
        
        if conversation_state["stage"] == "greeting":
            logger.info("Greeting from the agent")
            await asyncio.sleep(1)
            await session.generate_reply(instructions=agent.get_current_instructions(stage="greeting"))
            await asyncio.sleep(3)
            
    
    
    monitor_task=asyncio.create_task(monitor_conversation())

    while active_sessions.get(session_id, {}).get('status') != 'left':
            await asyncio.sleep(1)
            
    logger.info(f"🛑 User left, shutting down session {session_id}...")
    
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("🛑 Shutting down...")
    finally:
        # Cancel tasks
        
        if screen_task and not screen_task.done():
            screen_task.cancel()
            try:
                await screen_task
            except asyncio.CancelledError:
                pass
        
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        # Close session
        try:
            await session.close()
        except Exception as e:
            print(f"Error closing session: {e}")
        
        # Cleanup
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

        async with session_lock:
            if session_id in active_sessions:
                del active_sessions[session_id]


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint,api_key=LIVEKIT_API_KEY,api_secret=LIVEKIT_API_SECRET,ws_url=LIVEKIT_URL,))