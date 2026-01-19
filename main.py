import asyncio
from run_demo import run
from helper import narrate_step,is_demo_intent,narrate,create_browser_context,voice_generation
from voice_agent import voice_agent_workflow
from voice_process import record_audio,play_audio,speak,pcm16_base64
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import websockets
from config import OPENAI_WS,HEADERS,SAMPLE_RATE,agent,CHANNEL,BLOCK
import sounddevice as sd
import base64,json
import numpy as np
from openai import OpenAI
import collections
from agents.realtime import RealtimeRunner
from agent_voice_process import mic_cb,spk_cb,send_mic_audio,monitor_playback
from meet_interface import start_server,publish_screen_share_direct


BASE_DIR=Path(__file__).parent
URL="oncreate_agent_app.html"
UI_URL=BASE_DIR/URL
ONCREATE_MAIN_URL="https://www.oncreate.ai/"
JITSI_ROOM_URL = "https://meet.jit.si/MadRacingsTroubleReportedly"
ONCREATE_URL="http://agent.oncreate.ai/app.html"

client=OpenAI()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,slow_mo=5000)
        context = await browser.new_context()
        page =await context.new_page()
        await page.goto(ONCREATE_MAIN_URL,wait_until="domcontentloaded")
        await voice_generation(text="Hey, I am Oncreate's Demo agent so how can I help you today!")

        while True:
            audio = record_audio(seconds=5)
            user_text, response_text, demo_requested = voice_agent_workflow(audio)
            print("To start a demo",demo_requested)

            if demo_requested:
                async def on_step(step):
                    await narrate_step(step)

                await run(on_step)
            if not demo_requested:
                print("Agent:",response_text)

                play_audio("response.mp3")

            
            
        await browser.close()



# async def main_voice():
#     # async with RealtimeRunner(agent) as runner:
#     runner=RealtimeRunner(agent)
#     p,browser,page=await create_browser_context()
#     await page.goto(ONCREATE_MAIN_URL,wait_until="domcontentloaded")
#     demo_started = False
#     print("Voice assistant ready. Speak now...")

#     async for event in await runner.run():
        
#         # User finished speaking
#         if event.type == "transcript.final":
#             user_text = event.text
#             print("User:", user_text)

#             if not demo_started and is_demo_intent(user_text):
#                 demo_started = True

#                 await runner.say(
#                     "Sure. I will now demonstrate the application step by step."
#                 )
#                 async def on_step(step):
#                     # await narrate(step)
#                     await runner.say(step)

#                 asyncio.create_task(run(on_step))

#             elif not demo_started:
#                 # Normal conversation
#                 completion=client.chat.completions.create(
#                     model="gpt-4o",
#                     messages=[
#                         {
#                             "role":"system",
#                             "content":("You are a Oncreate  Product Demo AI  assistant. "
#                                         "If the user asks for a demo, confirm politely "
#                                         "and prepare to narrate an application walkthrough."
#                                         )
#                         },
#                         {
#                             "role":"user",
#                             "content":user_text
#                         }
#                     ]
#                 )
#                 response= completion.choices[0].message.content
                
#                 await runner.say(response)
#         await browser.close()





async def main_voice():
    try:
        # await publish_screen_share()
        await publish_screen_share_direct()

    except asyncio.CancelledError:
        pass






if __name__=="__main__":
    try:
        asyncio.run(main_voice())
        # asyncio.run(main_voice())
    except KeyboardInterrupt:
        print("program terminated by the user")