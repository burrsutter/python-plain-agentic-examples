
from dotenv import load_dotenv
from openai import OpenAI

import json

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

    
# Examples https://github.com/ibm-granite/granite-guardian/blob/main/cookbooks/granite-guardian-3.0/detailed_guide_ollama.ipynb

user_input = "Who are the current exhibiting artists?"
# ChatGPT 4o response from 5-basic-rag-like-artists.py
# assistant_response = """
# 0 Isabella Vanderwood
# 1 Elijah Montrose
# 2 Adelaide Delacroix
# """

# Other responses

# assistant_response = """
# """

assistant_response = """
Rembrandt
Michelangelo
Leonardo da Vinci
"""


def load_context():
    with open("museum.json", "r") as f:
        return json.load(f)

context_text = json.dumps(load_context())

system_test="groundedness"

riskycnt = 0
for i in range(3):
    completion = client.chat.completions.create(

        model=os.getenv("MODEL_NAME"), # granite3-guardian:8b-fp16
        messages=[
            {
                "role": "system",
                "content": system_test
            },
            {                
                "role": "context",
                "content": context_text,
            },
            {
                "role": "assistant",
                "content": assistant_response
            }
        ],        
    )
    response = completion.choices[0].message.content
    if (response == "Yes"): 
        riskycnt = riskycnt+1
    print(f"{response:<4} {riskycnt:<3}")

if(riskycnt >= 2):
    print("risk of", system_test)
else:
    print("No", system_test, "risk identified")

