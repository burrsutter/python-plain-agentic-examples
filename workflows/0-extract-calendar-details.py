from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from datetime import datetime

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

MODEL_NAME=os.getenv("MODEL_NAME")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the event")
    date: str = Field(
        description="Date and time of the event. Use ISO 8601 to format this value."
    )
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[str] = Field(description="List of participants")


today = datetime.now()
date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

# clear screen on Mac
os.system('clear')

# Likely a ready to book calendar event
user_input = "Invitation: Project Dance Program Meeting, April 15, 2025 at 2:00 PM Eastern"
# user_input = "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob to discuss the project roadmap."
# user_input = "Hey Alice and Bob, can we have a meeting tomorrow at 2pm?"
# user_input = "Hi Kef, I see you'll be in Stockholm at the next week and want to make sure we schedule some time for you to meet with the client. They're open all day Friday if you can make it happen."

# Possibly ready to book
# user_input = "Hi Dax, I see that your expense reports continue to contain elements that are now not part of our process. Instead of sending you a formal doc to read through to fix this moving forward, I'd like to get 5 minutes of your time sometime next week to make sure the new process is clear. I'm open any day but Friday. Fred"

# Less ready to book
# user_input = "Hi Burr, Saw your presentation Tuesday and would love to set up a time next week to meet and discuss opportunities at Acme Corp. Let me know what day/time might work for you."
# user_input = "Hi Lauren, The last new hire orientation went so well we'd love for you to do an information training for our HR team. Maybe a lunch and learn sometime next week? Let me know."

# Maybe not ready to book a specific calendar event/meeting
# user_input = "Please send me Alice and Bob's product roadmap presentation."
# user_input = "Happy Birthday!!! I hope you are well."


for i in range(5):
    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {"role": "user", "content": user_input},
        ],
        response_format=EventDetails,
    )

    parsed_event = completion.choices[0].message.parsed
    print("Event:", parsed_event.name, " Date:", parsed_event.date)

