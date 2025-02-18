from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import os
import json
import requests

load_dotenv()

import logging

# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# Step 1: Create client
# --------------------------------------------------------------


client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )


# --------------------------------------------------------------
# Step 2: Define the tool (function) that we want to call
# --------------------------------------------------------------

def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    logger.info("get_weather Tool invoked")    
    response = requests.get(
        # celsius, metric 
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        # fahrenheit, imperial
        # f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
    )
    data = response.json()
    return data["current"]


# --------------------------------------------------------------
# Step 3: Describe the get_weather tool 
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

# --------------------------------------------------------------
# Step 4: Call the model with the tool
# --------------------------------------------------------------


system_prompt = "You are a helpful weather assistant."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the temperature in Atlanta today?"},
]

completion_1 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# --------------------------------------------------------------
# Step 5: Debugging output
# --------------------------------------------------------------


logger.info("Tools to be invoked?")
logger.info(completion_1.choices[0].message.tool_calls)


# --------------------------------------------------------------
# Step 6: Execute get_weather function callback
# --------------------------------------------------------------


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)


if completion_1.choices[0].message.tool_calls:
    for tool_call in completion_1.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        logger.info("What? %s", completion_1.choices[0].message)
        messages.append(completion_1.choices[0].message)

        result = call_function(name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )

# --------------------------------------------------------------
# Step 7: Describe result and call model again
# --------------------------------------------------------------

class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )


completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    response_format=WeatherResponse,
)

# --------------------------------------------------------------
# Step 7: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed
# print(final_response)

logger.info("Temperature: %s", final_response.temperature)




