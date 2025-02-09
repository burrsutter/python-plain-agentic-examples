from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import logging

# Load env vars
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

MODEL_NAME=os.getenv("MODEL_NAME")

# clear screen on Mac
os.system('clear')

# --------------------------------------------------------------
# Step 1: Define the data models for each step
# --------------------------------------------------------------

class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(
        description="Does the text indicate a clear request to schedule a meeting or event at a specific date and time?"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the event")
    date: str = Field(
        description="Date and time of the event. Use ISO 8601 to format this value."
    )
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[str] = Field(description="List of participants")



# --------------------------------------------------------------
# Step 2: Define the functions
# --------------------------------------------------------------


def extract_event_info(user_input: str) -> EventExtraction:
    """First LLM call to determine if input is a calendar event"""
    logger.info("Starting event extraction analysis")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a calendar event.",
            },
            {"role": "user", "content": user_input},
        ],
        response_format=EventExtraction,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - Is calendar event: {result.is_calendar_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result


def parse_event_details(description: str) -> EventDetails:
    """Second LLM call to extract specific event details"""
    logger.info("Starting event details parsing")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Parsed event details - Name: {result.name}, Date: {result.date}, Duration: {result.duration_minutes}min"
    )
    logger.debug(f"Participants: {', '.join(result.participants)}")
    return result


# --------------------------------------------------------------
# Step 3: Chain the functions together
# --------------------------------------------------------------


def process_calendar_request(user_input: str):
    """Main function implementing the prompt chain with gate check"""
    logger.info("Processing calendar request")
    logger.info(f"Raw input: {user_input}")

    # First LLM call: Extract basic info
    initial_extraction = extract_event_info(user_input)

    # Gate check: Verify if it's a calendar event with sufficient confidence
    if (
        not initial_extraction.is_calendar_event
        or initial_extraction.confidence_score < 0.7
    ):
        logger.warning(
            f"Gate check failed - is_calendar_event: {initial_extraction.is_calendar_event}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None

    logger.info("Gate check passed, proceeding with event parsing")

    # Second LLM call: Get detailed event information
    event_details = parse_event_details(initial_extraction.description)

    logger.info("Calendar request processing completed successfully")
    

# --------------------------------------------------------------
# Step 4: Test the chain with a potential input
# --------------------------------------------------------------

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

# Not ready to book a specific calendar event/meeting
# user_input = "Please send me Alice and Bob's product roadmap presentation."
# user_input = "Happy Birthday!!! I hope you are well."

process_calendar_request(user_input)
