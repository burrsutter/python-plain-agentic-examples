from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

class AnalyzedEmail(BaseModel):
    reason: str
    sentiment: str
    customer_name: str
    email_address: str
    product_name: str
    escalate: bool

completion = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {"role": "system", "content": "Extract the support email information."},
        {
            "role": "user",
            "content": "Hello, I purchased a TechGear Pro Laptop, but I can't find the invoice in my email. Sincerely, David Jones david@example.org",
            # "content": "Hello, I purchased a TechGear Pro Laptop, but I can't find the invoice in my email and I need it immediately for tax purposes. Sincerely, David Jones david@example.org",
            # "content": "I purchased a TechGear Pro Laptop from you and the damn thing won't boot up, my project deadline is near. David david@example.org",
        },
    ],
    response_format=AnalyzedEmail,
)

emailanalysis = completion.choices[0].message.parsed

print("-------")
print(emailanalysis)
print("-------")
print("Reason:   ", emailanalysis.reason)
print("Customer: ", emailanalysis.customer_name)
print("Email:    ", emailanalysis.email_address)
print("Product:  ", emailanalysis.product_name)
print("Sentiment:", emailanalysis.sentiment)
print("Escalate: ", emailanalysis.escalate)

