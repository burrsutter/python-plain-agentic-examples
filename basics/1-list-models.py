
from dotenv import load_dotenv
from openai import OpenAI

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

# List available models
models = client.models.list()

# Print model IDs
for model in models.data:
    print(model.id)

