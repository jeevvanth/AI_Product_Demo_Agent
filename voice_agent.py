from openai import OpenAI
from helper import is_demo_intent
from dotenv import load_dotenv

load_dotenv()


client=OpenAI()



def voice_agent_workflow(audio_file: str):
    # Speech → Text
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=open(audio_file, "rb")
    )

    user_text = transcript.text
    print("User:", user_text)

    # LLM response
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Oncreate  Product Demo AI  assistant. "
                    "If the user asks for a demo, confirm politely "
                    "and prepare to narrate an application walkthrough."
                )
            },
            {"role": "user", "content": user_text}
        ]
    )

    response_text = completion.choices[0].message.content

    # Text → Speech
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=response_text
    )

    with open("response.mp3", "wb") as f:
        f.write(speech.read())

    return user_text, response_text, is_demo_intent(user_text)