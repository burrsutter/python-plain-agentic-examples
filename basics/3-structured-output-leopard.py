from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

class LeopardSpeed(BaseModel):
    speed: int


# notice "beta", "parse" and response_format
completion = client.beta.chat.completions.parse(
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

leopard = completion.choices[0].message.parsed

print("-------")
print("Speed: ", leopard.speed)
print("-------")

