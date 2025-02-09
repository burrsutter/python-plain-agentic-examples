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


class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(
        description="Does the text indicate a clear request to schedule a meeting or event at a specific date and time?"
        # description="Does this text describes a calendar event that needs to be scheduled?"
        # description="Does this text describes a ready to schedule calendar event"
        # description="Does this text describes a calendar event"
        # description="Whether this text describes a schedulable calendar event"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")


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
#user_input = "Hi Burr, Saw your presentation Tuesday and would love to set up a time next week to meet and discuss opportunities at Acme Corp. Let me know what day/time might work for you."
# user_input = "Hi Lauren, The last new hire orientation went so well we'd love for you to do an information training for our HR team. Maybe a lunch and learn sometime next week? Let me know."

# Maybe not ready to book a specific calendar event/meeting
# user_input = "Please send me Alice and Bob's product roadmap presentation."
# user_input = "Happy Birthday!!! I hope you are well."


for i in range(5):
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
          messages=[
              {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a calendar event.",
              },
              {
                "role": "user",
                "content": user_input
              },
            ],
            response_format=EventExtraction,
    )
    extracted_event = completion.choices[0].message.parsed
    print("Calendar Event:", extracted_event.is_calendar_event, " Confidence:", extracted_event.confidence_score)






