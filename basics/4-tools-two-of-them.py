from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from openai.types.chat import ChatCompletionMessage

import os
import json
import psycopg2
from psycopg2 import sql

import logging

# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()


client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )


DBNAME="northwind"
DBUSER="postgres"
DBPASSWORD="admin"
DBHOST="localhost"
DBPORT="5432"

system_prompt = "You are a helpful assistant"
user_input = "upper case the customer_id 'boTTm' and then find the customer by id in the database"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

class CustomerDetails(BaseModel):
    customer_id: str
    company_name: str
    contact_name: str
    country: str
    phone: str
    

# --------------------------------------------------------------
# Define the tools (functions) that we want to call
# --------------------------------------------------------------


def convert_to_uppercase(text):
    """Converts a given text to uppercase."""
    logger.info("converting %s to uppercase ", text)
    return text.upper()


def customer_search_by_id(customer_id):    
    logger.info("customer_search_by_id " + customer_id)

    connection = None
    cursor = None

    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=DBNAME,
            user=DBUSER,
            password=DBPASSWORD,
            host=DBHOST,
            port=DBPORT
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute a query to retrieve the desired customer        
        query = sql.SQL("SELECT customer_id, company_name, contact_name, country, phone FROM customers WHERE {id_field} = %s").format(            
            id_field=sql.Identifier('customer_id')
        )

        cursor.execute(query, (customer_id,))

        # Fetch all customer records
        customer = cursor.fetchone()

        # Display the list of customers
        logger.info("Database query found customer")        
        logger.info(customer)

        if customer:
            customer_data = {
                "customer_id": customer[0],
                "company_name": customer[1],
                "contact_name": customer[2],
                "country": customer[3],
                "phone": customer[4]
            }
            return json.dumps(customer_data)
        else:
            return json.dumps({"error": "Customer not found."})

    except Exception as error:
            print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        # Close the cursor and connection to clean up
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "convert_to_uppercase",
            "description": "Convert a given text to uppercase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to uppercase.",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type" : "function",
        "function" : {
            "name": "customer_search_by_id",
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
    },    
]


completion_1 = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    tool_choice="auto",        
    temperature=0.1
)

completion_1.model_dump()

# --------------------------------------------------------------
# Step 2: Debugging output
# --------------------------------------------------------------

# for debugging what is in messages
def log_messages(messages):
    logger.info("UNRAVELING messages BEGIN")
    logger.info(f"Total messages: {len(messages)}")

    for i, message in enumerate(messages):
            logger.info(f"Message {i + 1} - Type: {type(message)}")

            # If the message is a dictionary, print it nicely
            if isinstance(message, dict):
                logger.info(json.dumps(message, indent=4))  # Pretty print JSON
                
            # If it's a list, iterate over its items and print them
            elif isinstance(message, list):
                logger.info(f"List with {len(message)} items:")
                for j, item in enumerate(message):
                    logger.info(f"  Item {j + 1}: {item}")

            # If it's a ChatCompletionMessage, extract useful attributes
            elif isinstance(message, ChatCompletionMessage):                
                logger.info(f"Role: {message.role}")
                logger.info(f"Content: {message.content}")
                if message.tool_calls:
                    logger.info("Tool Calls:")
                    for tool_call in message.tool_calls:
                        logger.info(f"  - Name: {tool_call.function.name}")
                        logger.info(f"  - Arguments: {tool_call.function.arguments}")

            # If it's another type, just print it
            else:
                logger.info(f"Unknown type: {message}")

    logger.info("UNRAVELING messages END")


# --------------------------------------------------------------
# Step 3: Execute get_weather function
# --------------------------------------------------------------


def call_function(name, args):
    if name == "convert_to_uppercase":
        logger.info("calling convert_to_uppercase")
        return convert_to_uppercase(**args)
    if name == "customer_search_by_id":
        logger.info("calling customer_search_by_id")
        return customer_search_by_id(**args)


if completion_1.choices[0].message.tool_calls:
    for tool_call in completion_1.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        logger.info(name)

        messages.append(completion_1.choices[0].message)

        result = call_function(name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
        log_messages(messages)

# --------------------------------------------------------------
# Step 4: Call model again
# --------------------------------------------------------------

# completion_2 = client.chat.completions.create(
#     model=os.getenv("MODEL_NAME"),
#     messages=messages,
#     tools=tools,    
# )

# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

# response = completion_2.choices[0].message.content

# logger.info(response)




