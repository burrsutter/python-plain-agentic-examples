from calendar import month
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import json
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )


def search_kb(question: str):
    """
    Load the knowledge base from a JSON file. This is a mock tool with no semantic search/filtering
    """
    with open("museum.json", "r") as f:
        return json.load(f)

# print("*1" * 40)
# everything = search_kb("give me everything")
# print(json.dumps(everything))
# print("1" * 40)

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Get the answer to the user's question from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful assistant that answers questions from the knowledge base about our museum."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "what are the special events?"},
]

completion_1 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
)

def call_function(name, args):
    if name == "search_kb":
        return search_kb(**args)


for tool_call in completion_1.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion_1.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )

# after the tool has augmented the messages

# print("*2" * 40)
# content = json.loads(messages[3]['content'])
# for special_events in content['museum']['special_events']['events']:
#     print(special_events)
# print("*2" * 40)

# call the model again, with tool infused results

class Event(BaseModel):
    month: str
    name: str
    description: str
    
class SpecialEvents(BaseModel):
    events: List[Event]

completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    response_format=SpecialEvents,
)

final_response = completion_2.choices[0].message.parsed

print("*3" * 40)
# print(final_response)

for index, event in enumerate(final_response.events):
    print(event.month, "-" , event.name)
    print(event.description)

print("*3" * 40)
