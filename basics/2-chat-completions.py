from dotenv import load_dotenv
from openai import OpenAI

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

print(os.getenv("INFERENCE_SERVER_URL"))
print(os.getenv("MODEL_NAME"))

completion_1 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "What length of the Pont des Arts in meters?",
        },
    ],
    temperature=0.0, 
)

response = completion_1.choices[0].message.content

print(response)


completion_2 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),    
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "What is the top speed of a leopard in kilometers per hour?",
        },
    ],
    temperature=0.0, 
)

response = completion_2.choices[0].message.content

print(response)

# completion_3 = client.chat.completions.create(
#     model=os.getenv("MODEL_NAME"),    
#     messages=[
#         {"role": "system", "content": "You're a helpful assistant."},
#         {
#             "role": "user",
#             "content": "Who is Burr Sutter",
#         },
#     ],
# )

# response = completion_3.choices[0].message.content

# print(response)


