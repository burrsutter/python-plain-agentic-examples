from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from duckduckgo_search import DDGS
import os
import json
import requests
import logging

# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load .env file or env vars
load_dotenv()

# --------------------------------------------------------------
# I asked ChatGPT to give me a DuckDuckGo Tool calling example
# and combined it with Dave's example from https://www.youtube.com/watch?v=bZzyPscbtI8 
# --------------------------------------------------------------

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

MODEL_NAME=os.getenv("MODEL_NAME")

user_input = "What is the length of the Pont des Arts in meters?"


messages = [
    {"role": "system", "content": "You are a helpful assistant that must use DuckDuckGo to search the internet"},
    {"role": "user", "content": user_input}
]

class BridgeLength(BaseModel):
    length_in_meters: int



# --------------------------------------------------------------
# DuckDuckGo Search Tool
# --------------------------------------------------------------
def search_duckduckgo(query: str, num_results: int = 3):
    """Search DuckDuckGo and return top results."""
    # the next line was needed for llama3.2:3b-instruct-fp16
    num_results = int(num_results)  # Ensure it's an integer    
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=num_results))

    logger.info(json.dumps(results))
    return results  # Returns a list of dictionaries with search results


# Tool description/definition
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

# --------------------------------------------------------------
# Function Invoker
# --------------------------------------------------------------
def call_function(name, args):
    if name == "search_duckduckgo":
        logger.info("calling search_duckduckgo")
        return search_duckduckgo(**args)
    

# --------------------------------------------------------------
# LLM Call with Tools
# --------------------------------------------------------------
def llm_call_with_tools():
    completion_1 = client.chat.completions.create(
        model=MODEL_NAME, 
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.0, 
    )
        
    # generic tool callback invocation mechanism
    if completion_1.choices[0].message.tool_calls:
        logger.info("TOOLS: %s", completion_1.choices[0].message.tool_calls)
        for tool_call in completion_1.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # append the assistant's message
            messages.append(completion_1.choices[0].message)

            result = call_function(name, args)
                    
            # logger.info("-------------------------------------------------------------")
            # logger.info(json.dumps(result))
            # logger.info("-------------------------------------------------------------")
            
            # after the tool call, add to the messages array
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
            )
            logger.debug(messages)


# --------------------------------------------------------------
# Check messages to sought for user_input is "in there"
# --------------------------------------------------------------

# First try
# def verify_tool_response_with_llm(tool_response: str, user_input: str) -> bool:
#     """
#     Uses an LLM call to verify if the user_input exists in the tool's response.
#     """
#     verification_prompt = f"""
#     You are verifying a search result. Check if the following text contains the phrase:
#     '{user_input}'. Answer 'yes' or 'no'.

#     Text:
#     {tool_response}
#     """

#     # Call the LLM to analyze the response content
#     completion = client.chat.completions.create(
#         model=MODEL_NAME,  
#         messages=[{"role": "user", "content": verification_prompt}],
#         temperature=0.0, 
#     )

#     verification_result = completion.choices[0].message.content.lower().strip()

#     # Return True if LLM confirms the phrase exists
#     return "yes" in verification_result

# Improved
def verify_tool_response_with_llm(tool_response: str, user_input: str) -> bool:
    """
    Uses an LLM call to verify if the tool response contains relevant information
    related to the user's input, even if the exact phrase is not found.
    """
    verification_prompt = f"""
    You are an expert fact-checker. Your task is to determine whether the following text 
    contains information relevant to answering the question: "{user_input}".

    Do NOT look for an exact phrase match. Instead, check if the text provides useful 
    information related to the question, even if worded differently.

    Answer "yes" or "no".

    ----
    Text to analyze:
    {tool_response}
    ----
    """

    # Call the LLM to analyze the response content
    completion = client.chat.completions.create(
        model=MODEL_NAME,  
        messages=[{"role": "user", "content": verification_prompt}],
        temperature=0.0, 
    )

    verification_result = completion.choices[0].message.content.lower().strip()

    # Return True if LLM confirms the phrase exists in some form
    return "yes" in verification_result


# --------------------------------------------------------------
# Check messages to see if tool was invoked
# --------------------------------------------------------------
def check_messages_for_tools(messages, user_input) -> bool:
    tool_found = False
    keyword_verified = False

    for msg in messages:
        msg_dict = msg if isinstance(msg, dict) else msg.model_dump()

        if msg_dict.get("role") == "tool":
            tool_found = True
            tool_response = msg_dict.get("content", "")

            # Use LLM verification instead of simple string search
            keyword_verified = verify_tool_response_with_llm(tool_response, user_input)
            if keyword_verified:
                logger.info("✅ LLM confirmed the phrase exists in the tool response!")

    if tool_found and keyword_verified:
        return True
    elif tool_found:
        logger.warning("⚠️ Tool was used, but LLM did NOT confirm the phrase exists.")
        return False
    else:
        logger.warning("❌ Tool was NOT invoked.")
        return False

# --------------------------------------------------------------
# LLM Call with results of tool
# --------------------------------------------------------------
def llm_call_structured_output_bridge(messages) -> BridgeLength:

    completion_2 = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=messages,
        response_format=BridgeLength,
        temperature=0.0, 
    )

    return completion_2.choices[0].message.parsed
    


# --------------------------------------------------------------
# Main Stuff
# --------------------------------------------------------------

# Step 1 - initial LLM call to see if the tool, DuckDuckGo is used
llm_call_with_tools()

# Step 2 - verify that the tool found a valuable answer
search_results_good = check_messages_for_tools(messages, user_input)
logger.info(f"Search results are good? {search_results_good}")

# Step 3 - now call the LLM to extract the answer into structured output
if search_results_good:
    response = llm_call_structured_output_bridge(messages)
    logger.info("%s %d", user_input, response.length_in_meters)
else:
    logger.info(user_input)
    logger.info("no answer")
