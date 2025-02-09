from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

import os
import json


load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What are customer C100's details?"},
]

class CustomerDetails(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    balance: float

def fetch_customer_details(customer_id):
    """ this is mock data """
    print("fetch_customer_details invoked with " + customer_id)
    return "Customer " + customer_id + " is Burr Sutter with a balance of $100"


tools = [
    {
        "type" : "function",
        "function" : {
            "name": "fetch_customer_details",
            "description": "Find and return the customer details for the provided customer id",
            "parameters": {
                "type": "object",
                "properties" : {
                    "customer_id": {"type": "string", "description": "customers unique identifier string"},
                },
                "required": ["customer_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

# Make the request, passing in the tools defintion

completion = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),    
    messages=messages,
    tools=tools,
)

completion.model_dump()

# the callback

def call_function(name, args):
    if name == "fetch_customer_details":
        print("calling fetch_customer_details")
        return fetch_customer_details(**args)

# for debugging

def print_messages(messages):
    print("!!!!!")
    print(type(messages))  # identify type of object
    # print(json.dumps(messages)) # convert to JSON 
    print(messages)
    print("!!!!!")


# look inside the result for tool calls and make those tool calls

for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)
    result = call_function(name, args)
    print_messages(result)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )
    print_messages(messages)
    
# call the model again with the results of the tool/function call added

class CustomerDetails(BaseModel):
    customer_id: str
    customer_name: str
    balance: float


completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    response_format=CustomerDetails
)

final_response = completion_2.choices[0].message.parsed
print("-------")
print(final_response.customer_id)
print(final_response.customer_name)
print(final_response.balance)

# and another call to the model, to see if it does NOT use the tool

class LeopardSpeed(BaseModel):
    speed: int

completion_3 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "What is the top speed of a leopard in kilometers per hour?",
        },
    ],
    response_format=LeopardSpeed,
)

result = completion_3.choices[0].message.parsed

print("Leopard Speed: ", result.speed)

