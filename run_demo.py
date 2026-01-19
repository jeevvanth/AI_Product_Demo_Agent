from playwright.async_api import async_playwright
from pathlib import Path
import time
import asyncio
from enumerate import DemoStep
from helper import voice_generation
from cursor import inject_cursor_styles, type_with_cursor,click_with_cursor,set_cursor_mode,select_option_with_cursor,hover_dropdown_option,scroll_with_cursor,scroll_to_element_with_cursor
from realtime_websocket import RealtimeTTS
import logging
from agent_instruction import DemoAgent



BASE_DIR=Path(__file__).parent
URL="oncreate_agent_app.html"
UI_URL=BASE_DIR/URL
ONCREATE_URL="http://agent.oncreate.ai/app.html"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)
agent=DemoAgent()
# tmpl = """You are a text to speech that narrates exactly in the  user_text. You should only say what is in the user_text .you should not add extra words  apart from the user_text while narrating  :{user_text}."""
tmpl=agent.get_current_instructions(stage="demo")


async def run(page,browser,session):

        
        # await page.goto(UI_URL, wait_until="domcontentloaded")
        print("Entered the Demo")
        logger.info("Connecting to TTS WebSocket...")
        
        # await tts.speak(text="I am starting the application demo now.")
        instructions = tmpl.format(user_text="i am starting the application demo now")
        await session.generate_reply(instructions=instructions)
        await page.goto(ONCREATE_URL, wait_until="domcontentloaded")
        
        await inject_cursor_styles(page)
        await set_cursor_mode(page,mode="arrow")

        # await on_step(DemoStep.CREATE_AGENT)
        # await tts.speak(text="First, I create a new AI agent.")
        instructions = tmpl.format(user_text="First, I create a new AI agent.")
        await session.generate_reply(instructions=instructions)
        # await page.get_by_role("button", name="+ New Agent").click()
        await click_with_cursor(page, 'button:has-text("+ New Agent")')


        # await on_step(DemoStep.OVERALL)
        # await tts.speak(text="Here I fill in the basic agent information.")
        instructions = tmpl.format(user_text="Here I fill in the basic agent information.")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-tab="tab-overall"]')
        await click_with_cursor(page, 'button[data-tab="tab-overall"]')

        TYPE_DELAY = 60
        
        # await page.type("#field-display-name", "Product demo", delay=TYPE_DELAY)
        await type_with_cursor(page, "#field-display-name", "Product demo", TYPE_DELAY)
        # await on_step(DemoStep.DISPLAY_NAME)
        # await tts.speak(text="Entered the ai agent name here")
        instructions = tmpl.format(user_text="Entered the ai agent name here")
        await session.generate_reply(instructions=instructions)

        # await on_step(DemoStep.PRESENTATION_MSG)
        # await tts.speak(text="I am going to enter the presentation message to for the ai agent")
        instructions = tmpl.format(user_text="I am going to enter the presentation message to for the ai agent")
        await session.generate_reply(instructions=instructions)
        # await page.type(
        #     "#field-presentation",
        #     "its a greate for personal uses",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-presentation", "Hello! I'm your AI assistant from OnCreate. How can I help you today?", TYPE_DELAY)

        # await on_step(DemoStep.GOAL)
        # await tts.speak(text="I am going to enter the goal here.")
        instructions = tmpl.format(user_text="I am going to enter the goal here.")
        await session.generate_reply(instructions=instructions)
        # await page.type(
        #     "#field-goal",
        #     "to make a greater a product and get a greate impression",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page,"#field-goal",
                               "Your goal is to showcase the OnCreate platform, qualify the user, and walk them through the product demo.", TYPE_DELAY)

        # await on_step(DemoStep.TONE)
        # await tts.speak(text="Next I am going to enter the tone the define the ai agent will be speaking")
        instructions = tmpl.format(user_text="Next I am going to enter the tone the define the ai agent will be speaking")
        await session.generate_reply(instructions=instructions)
        # await page.type(
        #     "#field-tone",
        #     "to make a greater a product and get a greate impression",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page,"#field-tone", 
                               "Friendly, professional, and concise. Speak like a human, not a robot.", TYPE_DELAY)

        await scroll_with_cursor(page,direction="bottom",duration=1500,container_selector='.content-scroll')

        await page.wait_for_timeout(500)

        
        # await tts.speak(text="Next I am going to enter the qualification question by questioning the company.") 
        instructions = tmpl.format(user_text="Next I am going to enter the qualification question by questioning the company.")
        await session.generate_reply(instructions=instructions)
        # await page.type(
        #     "#field-questions",
        #     "What is your company size? What is your budget range? What is your timeline for implementation?",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-questions",
                              "What is your company size? What is your budget range? What is your timeline for implementation?", TYPE_DELAY)
        
        await scroll_to_element_with_cursor(page=page,selector="#field-closing",container_selector='.content-scroll')

        
        # await tts.speak(text="Finally I am going to write the closing behaviour.")
        instructions = tmpl.format(user_text="Finally I am going to write the closing behaviour.")
        await session.generate_reply(instructions=instructions)
        # await page.type(
        #     "#field-closing",
        #     "Ask if they have any final questions. If not, propose the next step: booking a live call with the OnCreate team.",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-closing",
                              "Ask if they have any final questions. If not, propose the next step: booking a live call with the OnCreate team.", TYPE_DELAY)
        
        await scroll_with_cursor(page,direction="top",duration=1500,container_selector='.content-scroll')

        
        # await page.click('button[data-tab="tab-voice"]')
        # await tts.speak(text="Next, I am going to the voice section")
        instructions = tmpl.format(user_text="Next, I am going to the voice section")
        await session.generate_reply(instructions=instructions)
        await click_with_cursor(page, 'button[data-tab="tab-voice"]')
        # await on_step(DemoStep.VOICE)
        # await tts.speak(text="Configuring voice and language")
        # await session.generate_reply(
        #     instructions="Say: 'Configuring voice and language.'")
        instructions = tmpl.format(user_text="Configuring voice and language.")
        await session.generate_reply(instructions=instructions)

        # await page.click("#field-language")
        await click_with_cursor(page, "#field-language")

        # await tts.speak(text="These are the Languages I can able to speak")
        instructions = tmpl.format(user_text="These are the Languages I can able to speak")
        await session.generate_reply(instructions=instructions)

        await page.wait_for_timeout(300)

        await page.wait_for_selector("#field-language")
        # await hover_dropdown_option(page,"#field-language")
        await page.select_option("#field-language", label="German")
        # await select_option_with_cursor(page,"#field-language","German")
        # await on_step(DemoStep.LANGUAGE)
        await page.click("#field-language")
        # await click_with_cursor(page, "#field-language")
        
        # await page.click("#field-voice")
        await click_with_cursor(page, "#field-voice")
        
        # await tts.speak(text="These are the types of voices I can able to speak")
        instructions = tmpl.format(user_text="These are the types of voices I can able to speak")
        await session.generate_reply(instructions=instructions)
        # await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        await page.wait_for_selector("#field-voice")
        # await hover_dropdown_option(page,"#field-voice")
        await page.select_option("#field-voice", label="Arjun (Indian Male)")
        # await select_option_with_cursor(page,"#field-voice","Arjun (Indian Male)")
        
        
        # await tts.speak(text="Here I am going to Choose Arjun's voice here")
        instructions = tmpl.format(user_text="Here I am going to Choose Arjun's voice here")
        await session.generate_reply(instructions=instructions)
        await page.wait_for_timeout(300)
        await page.click("#field-voice")
        # await click_with_cursor(page, "#field-voice")

        # await page.wait_for_timeout(500)
        await page.wait_for_timeout(200)
        # await tts.speak(text="Next, I am going for the knowledge base")
        instructions = tmpl.format(user_text="Next, I am going for the knowledge base")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-tab="tab-knowledge"]')
        await click_with_cursor(page, 'button[data-tab="tab-knowledge"]')
     
        # await tts.speak(text="Now I review the knowledge settings.")
        instructions = tmpl.format(user_text="Now I review the knowledge settings.")
        await session.generate_reply(instructions=instructions)
        # await page.wait_for_timeout(500)
        # await on_step(DemoStep.KNOWLEDGE_BASE)
        # await tts.speak(text="Here is the knowledge base that I have and act for your required process")
        instructions = tmpl.format(user_text="Here is the knowledge base that I have and act for your required process")
        await session.generate_reply(instructions=instructions)

        # await tts.speak(text="Next, I am going for the session overview")
        instructions = tmpl.format(user_text="Next, I am going for the session overview")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-tab="tab-sessions"]')
        await click_with_cursor(page, 'button[data-tab="tab-sessions"]')
        # await on_step(DemoStep.SESSIONS)
        # await tts.speak(text="This section manages agent sessions.")
        instructions = tmpl.format(user_text="This section manages agent sessions.")
        await session.generate_reply(instructions=instructions)

        await scroll_with_cursor(page, direction='bottom', duration=1500, container_selector='.content-scroll')
        await page.wait_for_timeout(500)
        await scroll_with_cursor(page, direction='top', duration=1500, container_selector='.content-scroll')
       
        # await tts.speak(text="Here you can see all the transcripts, screen records of this session and email IDs of participants")
        instructions = tmpl.format(user_text="Here you can see all the transcripts, screen records of this session and email IDs of participants")
        await session.generate_reply(instructions=instructions)

        
        # await tts.speak(text="Here are advanced configuration options.")
        instructions = tmpl.format(user_text="Here are advanced configuration options.")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-tab="tab-advanced"]')
        await click_with_cursor(page, 'button[data-tab="tab-advanced"]')

        # await tts.speak(text="Now I am going back to the homepage")
        instructions = tmpl.format(user_text="Now I am going back to the homepage")
        await session.generate_reply(instructions=instructions)
        # await page.get_by_role("button", name="Back to Agents").click()
        await click_with_cursor(page, 'button:has-text("Back to Agents")')
        

        # await tts.speak(text="Next I am going to Analytics page")
        instructions = tmpl.format(user_text="Next I am going to Analytics page")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-title="Analytics"]')
        await click_with_cursor(page, 'button[data-title="Analytics"]')
        # await tts.speak(text="Here are the session analytics,rate,duration")
        instructions = tmpl.format(user_text="Here are the session analytics,rate,duration")
        await session.generate_reply(instructions=instructions)

        # await tts.speak(text="Next I am going to Integration page")
        instructions = tmpl.format(user_text="Next I am going to Integration page")
        await session.generate_reply(instructions=instructions)
        # await page.click('button[data-title="Integrations"]')
        await click_with_cursor(page, 'button[data-title="Integrations"]')
        # await tts.speak(text="Here are the integration I can able to integrate into the product demo.")
        instructions = tmpl.format(user_text="Here are the integration I can able to integrate into the product demo.")
        await session.generate_reply(instructions=instructions)
        
        # await tts.speak("if you want to go futhur please connect with our team and schedule a meet , meet link is in the chat section, Thank you have a nice day")
        instructions = tmpl.format(user_text="if you want to go futhur please connect with our team and schedule a meet , meet link is in the chat section, Thank you have a nice day.")
        await session.generate_reply(instructions=instructions)

        # time.sleep(30)    
        # await tts.close()
        await asyncio.sleep(5) 
        await browser.close()








async def run_the_demo(page,browser):


        tts=RealtimeTTS()
        
        # await page.goto(UI_URL, wait_until="domcontentloaded")
        print("Entered the Demo")
        await tts.connect()
        await tts.speak(text="I am starting the application demo now.")
        
        # await page.goto(ONCREATE_URL, wait_until="domcontentloaded")
        
        await inject_cursor_styles(page)
        await set_cursor_mode(page,mode="arrow")

        # await on_step(DemoStep.CREATE_AGENT)
        await tts.speak(text="First, I create a new AI agent.")
       
        # await page.get_by_role("button", name="+ New Agent").click()
        await click_with_cursor(page, 'button:has-text("+ New Agent")')


        # await on_step(DemoStep.OVERALL)
        await tts.speak(text="Here I fill in the basic agent information.")
        
        # await page.click('button[data-tab="tab-overall"]')
        await click_with_cursor(page, 'button[data-tab="tab-overall"]')

        TYPE_DELAY = 60
        
        # await page.type("#field-display-name", "Product demo", delay=TYPE_DELAY)
        await type_with_cursor(page, "#field-display-name", "Product demo", TYPE_DELAY)
        # await on_step(DemoStep.DISPLAY_NAME)
        await tts.speak(text="Entered the ai agent name here")
        

        # await on_step(DemoStep.PRESENTATION_MSG)
        await tts.speak(text="I am going to enter the presentation message to for the ai agent")
        
        # await page.type(
        #     "#field-presentation",
        #     "its a greate for personal uses",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-presentation", "Hello! I'm your AI assistant from OnCreate. How can I help you today?", TYPE_DELAY)

        # await on_step(DemoStep.GOAL)
        await tts.speak(text="I am going to enter the goal here.")
        
        # await page.type(
        #     "#field-goal",
        #     "to make a greater a product and get a greate impression",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page,"#field-goal",
                               "Your goal is to showcase the OnCreate platform, qualify the user, and walk them through the product demo.", TYPE_DELAY)

        # await on_step(DemoStep.TONE)
        await tts.speak(text="Next I am going to enter the tone the define the ai agent will be speaking")
        # await page.type(
        #     "#field-tone",
        #     "to make a greater a product and get a greate impression",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page,"#field-tone", 
                               "Friendly, professional, and concise. Speak like a human, not a robot.", TYPE_DELAY)

        await scroll_with_cursor(page,direction="bottom",duration=1500,container_selector='.content-scroll')

        await page.wait_for_timeout(500)

        
        await tts.speak(text="Next I am going to enter the qualification question by questioning the company.") 
        # await page.type(
        #     "#field-questions",
        #     "What is your company size? What is your budget range? What is your timeline for implementation?",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-questions",
                              "What is your company size? What is your budget range? What is your timeline for implementation?", TYPE_DELAY)
        
        await scroll_to_element_with_cursor(page=page,selector="#field-closing",container_selector='.content-scroll')

        
        await tts.speak(text="Finally I am going to write the closing behaviour.")
        # await page.type(
        #     "#field-closing",
        #     "Ask if they have any final questions. If not, propose the next step: booking a live call with the OnCreate team.",
        #     delay=TYPE_DELAY
        # )
        await type_with_cursor(page, "#field-closing",
                              "Ask if they have any final questions. If not, propose the next step: booking a live call with the OnCreate team.", TYPE_DELAY)
        
        await scroll_with_cursor(page,direction="top",duration=1500,container_selector='.content-scroll')

        
        # await page.click('button[data-tab="tab-voice"]')
        await tts.speak(text="Next, I am going to the voice section")
        await click_with_cursor(page, 'button[data-tab="tab-voice"]')
        # await on_step(DemoStep.VOICE)
        await tts.speak(text="Configuring voice and language")

        # await page.click("#field-language")
        await click_with_cursor(page, "#field-language")

        await tts.speak(text="These are the Languages I can able to speak")

        await page.wait_for_timeout(500)

        await page.wait_for_selector("#field-language")
        # await hover_dropdown_option(page,"#field-language")
        await page.select_option("#field-language", label="German")
        # await select_option_with_cursor(page,"#field-language","German")
        # await on_step(DemoStep.LANGUAGE)
        await click_with_cursor(page, "#field-language")
        
        
        # await page.click("#field-voice")
        await click_with_cursor(page, "#field-voice")
        
        await tts.speak(text="These are the types of voices I can able to speak")
        await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        await page.wait_for_selector("#field-voice")
        # await hover_dropdown_option(page,"#field-voice")
        await page.select_option("#field-voice", label="Arjun (Indian Male)")
        # await select_option_with_cursor(page,"#field-voice","Arjun (Indian Male)")
        
        await tts.speak(text="Here I am going to Choose Arjun's voice here")
        await page.wait_for_timeout(300)
        await click_with_cursor(page, "#field-voice")

        # await page.wait_for_timeout(500)
        await page.wait_for_timeout(200)
        await tts.speak(text="Next, I am going for the knowledge base")
        # await page.click('button[data-tab="tab-knowledge"]')
        await click_with_cursor(page, 'button[data-tab="tab-knowledge"]')
     
        await tts.speak(text="Now I review the knowledge settings.")
        await page.wait_for_timeout(500)
        # await on_step(DemoStep.KNOWLEDGE_BASE)
        await tts.speak(text="Here is the knowledge base that I have and act for your required process")

        await tts.speak(text="Next, I am going for the session overview")
        # await page.click('button[data-tab="tab-sessions"]')
        await click_with_cursor(page, 'button[data-tab="tab-sessions"]')
        # await on_step(DemoStep.SESSIONS)
        await tts.speak(text="This section manages agent sessions.")

        await scroll_with_cursor(page, direction='bottom', duration=1500, container_selector='.content-scroll')
        await page.wait_for_timeout(500)
        await scroll_with_cursor(page, direction='top', duration=1500, container_selector='.content-scroll')
       
        await tts.speak(text="Here you can see all the transcripts, screen records of this session and email IDs of participants")
        await page.wait_for_timeout(500)
        await tts.speak(text="Here are advanced configuration options.")
        # await page.click('button[data-tab="tab-advanced"]')
        await click_with_cursor(page, 'button[data-tab="tab-advanced"]')

        await tts.speak(text="Now I am going back to the homepage")
        # await page.get_by_role("button", name="Back to Agents").click()
        await click_with_cursor(page, 'button:has-text("Back to Agents")')
        

        await tts.speak(text="Next I am going to Analytics page")
        
        # await page.click('button[data-title="Analytics"]')
        await click_with_cursor(page, 'button[data-title="Analytics"]')
        await tts.speak(text="Here are the session analytics,rate,duration")
        

        # await tts.speak(text="Next I am going to Integration page")
        # await page.click('button[data-title="Integrations"]')
        await click_with_cursor(page, 'button[data-title="Integrations"]')
        await tts.speak(text="Here are the integration I can able to integrate into the product demo.")
        
        
        await tts.speak("if you want to go futhur please connect with our team and schedule a meet , meet link is in the chat section, Thank you have a nice day")

        # time.sleep(30)    
        await tts.close()
        await asyncio.sleep(5) 

        await browser.close()

        


# if __name__=="__main__":
#         try:
#              asyncio.run(run())
#         except Exception as e:
#              raise e