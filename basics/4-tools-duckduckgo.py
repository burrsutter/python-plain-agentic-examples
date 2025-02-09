from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS
import os
import json
import requests

load_dotenv()

# --------------------------------------------------------------
# I asked ChatGPT to give me a DuckDuckGo Tool calling example
# and combined it with Dave E's example
# --------------------------------------------------------------

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

messages = [
    {"role": "system", "content": "You are a helpful assistant that can use DuckDuckGo to search the internet"},
    {"role": "user", "content": "What is the top speed of a leopard in kilometers per hour?"},
]


# Define the function for DuckDuckGo search
def search_duckduckgo(query: str, num_results: int = 3):
    """Search DuckDuckGo and return top results."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=num_results))
    
    return results  # Returns a list of dictionaries with search results

# Define OpenAI tool (function calling)
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_duckduckgo",
            "description": "Search DuckDuckGo and return web results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results to return", "default": 3},
                },
                "required": ["query"]
            },
        },
    }
]

# Call OpenAI to trigger function
completion_1 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"), 
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# function invoker
def call_function(name, args):
    if name == "search_duckduckgo":
        print("calling search_duckduckgo")
        return search_duckduckgo(**args)
    
# for debugging
def print_messages(messages):
    print("!!!!!")
    print(type(messages))
    print(messages)
    print("!!!!!")
    
# generic tool callback invocation mechanism
if completion_1.choices[0].message.tool_calls:
    for tool_call in completion_1.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion_1.choices[0].message)
        result = call_function(name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
        print_messages(messages)


# now call the model again, with the results of the tool invocation

class LeopardSpeed(BaseModel):
    topspeed: int

completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    response_format=LeopardSpeed,
)


response = completion_2.choices[0].message.content
print("------------")
print("Final Answer: ", response)
print("------------")


