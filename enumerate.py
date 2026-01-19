from enum import Enum

class DemoStep(Enum):
    START = "Starting the application demo"
    CREATE_AGENT = "Creating a new AI agent"

    OVERALL = "Filling overall agent details."
    DISPLAY_NAME="Entered the ai agent name here."
    PRESENTATION_MSG="Im going to enter the presentation message to for the ai agent."
    GOAL="Im going to enter the goal here."
    TONE="Next Im going to enter the tone the define the ai agent will be speaking."
    QUALIFICATION="Next Im going to enter the qualification question by questioning the company."
    CLOSING_BEHAVIOUR="Finally Im going to write the closing behaviour."

    VOICE = "Configuring voice and language"
    LANGUAGE_DROPDOWN="These are the Languages I can able to speak"
    LANGUAGE="Im going to choose German here"
    VOICE_DROPDOWN="These are the types of voices I can able to speak"
    VOICE_SELECTION="Here I am going to Choose Arjun's voice here"

    KNOWLEDGE = "Reviewing knowledge section"
    KNOWLEDGE_BASE="Here are the knnowledge base that I have and act for your required process"

    SESSIONS = "Checking sessions"
    SESSION_OVERVIEW="Here you can see all the transcripts ,screen record of this session and email ids who are participated in this session"

    ADVANCED = "Exploring advanced options"
    COMPLETE = "Demo completed"
