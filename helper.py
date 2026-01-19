from enumerate import DemoStep
from openai import OpenAI
from voice_process  import play_audio,speak
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import json
from realtime_websocket import RealtimeTTS


load_dotenv()

client=OpenAI()

VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 720

tts=RealtimeTTS()

def is_demo_intent(text: str) -> bool:
    # keywords = [
    #     "show",
    #     "demo",
    #     "demonstrate",
    #     "product",
    #     "application"
    # ]
    # text = text.lower()
    # return any(k in text for k in keywords)

    completion=client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role":"system",
                            "content":"""You are a helpful assistant that determines if the user wants to see a product demo or demonstration or application review . 
                            you might get the text in different languages so you should be able to understand multiple languages .
                            you should analyze the user message and respond with a bool value "True" or "False" only."""
                        },
                        {
                            "role":"user",
                            "content":text
                        }
                    ]
                )
    response= completion.choices[0].message.content
    print("Demo Intent Response:",response)
    # result:bool= response.strip()
    if response=="True":
        return True
    else:
        return False
    


async def narrate_step(step: DemoStep):
    narration = {
        DemoStep.START: "I am starting the application demo now.",
        DemoStep.CREATE_AGENT: "First, I create a new AI agent.",
        DemoStep.OVERALL: "Here I fill in the basic agent information.",
        DemoStep.DISPLAY_NAME:"Entered the ai agent name here",
        DemoStep.PRESENTATION_MSG:"I am going to enter the presentation message to for the ai agent",
        DemoStep.GOAL:"I am going to enter the goal here.",
        DemoStep.TONE:"Next I am going to enter the tone the define the ai agent will be speaking",
        DemoStep.QUALIFICATION:"Next I am going to enter the qualification question by questioning the company ",
        DemoStep.CLOSING_BEHAVIOUR:"Finally I am going to write the closing behaviour",
        DemoStep.VOICE: "Next, I configure the voice and language.",
        DemoStep.LANGUAGE_DROPDOWN:"These are the Languages I can able to speak",
        DemoStep.LANGUAGE:"I am going to choose German here",
        DemoStep.VOICE_DROPDOWN:"These are the types of voices I can able to speak",
        DemoStep.VOICE_SELECTION:"Here I am going to Choose Arjun's voice here",
        DemoStep.KNOWLEDGE: "Now I review the knowledge settings.",
        DemoStep.KNOWLEDGE_BASE:"Here are the knnowledge base that I have and act for your required process",
        DemoStep.SESSIONS: "This section manages agent sessions.",
        DemoStep.SESSION_OVERVIEW:"Here you can see all the transcripts ,screen record of this session and email ids who are participated in this session",
        DemoStep.ADVANCED: "Here are advanced configuration options.",
        DemoStep.COMPLETE: "This concludes the demonstration and Have a nice day."
    }

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=narration[step]
    )

    with open("step.mp3", "wb") as f:
        f.write(speech.read())

    play_audio("step.mp3")





async def voice_generation(text:str):
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=text
    )

    with open("step.mp3", "wb") as f:
        f.write(speech.read())

    play_audio("step.mp3")




async def narrate(ws,step:DemoStep):
    narration = {
        DemoStep.START: "I am starting the application demo now.",
        DemoStep.CREATE_AGENT: "First, I create a new AI agent.",
        DemoStep.OVERALL: "Here I fill in the basic agent information.",
        DemoStep.DISPLAY_NAME:"Entered the ai agent name here",
        DemoStep.PRESENTATION_MSG:"I am going to enter the presentation message to for the ai agent",
        DemoStep.GOAL:"I am going to enter the goal here.",
        DemoStep.TONE:"Next I am going to enter the tone the define the ai agent will be speaking",
        DemoStep.QUALIFICATION:"Next I am going to enter the qualification question by questioning the company ",
        DemoStep.CLOSING_BEHAVIOUR:"Finally I am going to write the closing behaviour",
        DemoStep.VOICE: "Next, I configure the voice and language.",
        DemoStep.LANGUAGE_DROPDOWN:"These are the Languages I can able to speak",
        DemoStep.LANGUAGE:"I am going to choose German here",
        DemoStep.VOICE_DROPDOWN:"These are the types of voices I can able to speak",
        DemoStep.VOICE_SELECTION:"Here I am going to Choose Arjun's voice here",
        DemoStep.KNOWLEDGE: "Now I review the knowledge settings.",
        DemoStep.KNOWLEDGE_BASE:"Here are the knnowledge base that I have and act for your required process",
        DemoStep.SESSIONS: "This section manages agent sessions.",
        DemoStep.SESSION_OVERVIEW:"Here you can see all the transcripts ,screen record of this session and email ids who are participated in this session",
        DemoStep.ADVANCED: "Here are advanced configuration options.",
        DemoStep.COMPLETE: "This concludes the demonstration and Have a nice day."
    }

    await speak(ws, narration[step])


async def narrate_with_ws(step: DemoStep):
    """Narrate demo steps using the existing RealtimeRunner session"""
    narration = {
        DemoStep.START: "I am starting the application demo now.",
        DemoStep.CREATE_AGENT: "First, I create a new AI agent.",
        DemoStep.OVERALL: "Here I fill in the basic agent information.",
        DemoStep.DISPLAY_NAME: "Entered the ai agent name here",
        DemoStep.PRESENTATION_MSG: "I am going to enter the presentation message for the ai agent",
        DemoStep.GOAL: "I am going to enter the goal here.",
        DemoStep.TONE: "Next I am going to enter the tone that defines how the ai agent will be speaking",
        DemoStep.QUALIFICATION: "Next I am going to enter the qualification question by questioning the company",
        DemoStep.CLOSING_BEHAVIOUR: "Finally I am going to write the closing behaviour",
        DemoStep.VOICE: "Next, I configure the voice and language.",
        DemoStep.LANGUAGE_DROPDOWN: "These are the Languages I can speak",
        DemoStep.LANGUAGE: "I am going to choose German here",
        DemoStep.VOICE_DROPDOWN: "These are the types of voices I can speak",
        DemoStep.VOICE_SELECTION: "Here I am going to Choose Arjun's voice",
        DemoStep.KNOWLEDGE: "Now I review the knowledge settings.",
        DemoStep.KNOWLEDGE_BASE: "Here is the knowledge base that I have and act for your required process",
        DemoStep.SESSIONS: "This section manages agent sessions.",
        DemoStep.SESSION_OVERVIEW: "Here you can see all the transcripts, screen records of this session and email IDs of participants",
        DemoStep.ADVANCED: "Here are advanced configuration options.",
        DemoStep.COMPLETE: "This concludes the demonstration. Have a nice day."
    }
    
    await tts.connect()
    await tts.speak(narration[step])
    # await tts.close()


async def create_browser_context():
    p=await async_playwright().start()
    browser=await p.chromium.launch(headless=False,slow_mo=5000)
    # context =await browser.new_context(permissions=["microphone", "camera"])
    context =await browser.new_context()
    page =await context.new_page()

    return p,browser,page,context