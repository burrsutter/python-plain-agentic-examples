from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError
import os
import json
load_dotenv()

API_KEY=os.getenv("API_KEY")
INFERENCE_SERVER_URL=os.getenv("INFERENCE_SERVER_URL")
MODEL_NAME=os.getenv("MODEL_NAME")

client = OpenAI(
    api_key=API_KEY,
    base_url=INFERENCE_SERVER_URL
    )


print(INFERENCE_SERVER_URL)
print(MODEL_NAME)


class PythonCode(BaseModel):
    python_code: str


sys_prompt="Analyze the provided JSON and create the python code needed to extract the seller information from the JSON. The JSON is a DoclingDocument object. The seller information is usually found in the body of the document, and it may be labeled as 'Seller:' or similar. The output should be a Python function that takes the JSON as input and returns the seller information as a string."


JSON_FILE = "../output.json"  # The JSON file to read from

def open_json_file(json_file_path: str):
    """Opens a JSON file and returns its content."""
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return None

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return None
    

data = open_json_file(JSON_FILE)
print(f"JSON: \n {data}")


completion = client.beta.chat.completions.parse(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": sys_prompt},
        {
            "role": "user",
            "content": data,
        },
    ],
    response_format=PythonCode,
)

pythoncode = completion.choices[0].message.parsed

print(pythoncode)

