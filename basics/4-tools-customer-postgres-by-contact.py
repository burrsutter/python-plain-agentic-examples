from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import BaseModel
from typing import List

import psycopg2
from psycopg2 import sql
import os
import json
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


contact_name_to_find = "Elizabeth"
user_input = "Find all customers with contact name " + contact_name_to_find

# this list serves as a memory bank, allowing for multiple LLM calls
messages = [
    {"role": "system", "content": "You are a helpful assistant that must customer_search or contact_search tool"},
    {"role": "user", "content": user_input}
]


class CustomerDetails(BaseModel):
    customer_id: str
    company_name: str
    contact_name: str
    country: str
    phone: str

class CustomerList(BaseModel):
    customers: List[CustomerDetails]    

def find_all_customers_by_contact_name(contact_name):    
    logger.info("find_all_customers_by_contact_name " + contact_name)

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

        # Execute a query to retrieve the desired customers by contact name        
        query = sql.SQL("""
        SELECT customer_id, company_name, contact_name, country, phone
        FROM customers
        WHERE contact_name ILIKE %s
        """)

        cursor.execute(query, ('%' + contact_name + '%',))

        # Fetch all customer records
        customers = cursor.fetchall()

        # Display the list of customers
        
        

        if customers:
            customers_list = [
                CustomerDetails(
                    customer_id=customer[0],
                    company_name=customer[1],
                    contact_name=customer[2],
                    country=customer[3],
                    phone=customer[4]
                )
                for customer in customers
            ]
            logger.info("Database query found customer(s):")
            for customer in customers_list:                
                logger.info("Customer ID: %s, Company Name: %s", customer.customer_id, customer.company_name)
            return json.dumps([customer.model_dump() for customer in customers_list])
        else:
            return json.dumps({"error": "no customers found."})

    except Exception as error:
            print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        # Close the cursor and connection to clean up
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    


tools = [
    {
        "type" : "function",
        "function" : {
            "name": "find_all_customers_by_contact_name",
            "description": "Find and return all customer details by contact name",
            "parameters": {
                "type": "object",
                "properties" : {
                    "contact_name": {"type": "string", "description": "contact name"},
                },
                "required": ["contact_name"],
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
    # tool_choice="required", # works with openai.com and ollama, not vLLM
    tool_choice="auto",
    temperature=0.1
)

completion.model_dump()

# the callback

def call_function(name, args):
    if name == "find_all_customers_by_contact_name":
        logger.info("calling find_all_customers_by_contact_name")
        return find_all_customers_by_contact_name(**args)


# for debugging what is in messages
def log_messages(messages):
    logger.info("********************")
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

    logger.info("********************")

# look inside the result for tool calls and make those tool calls

if completion.choices[0].message.tool_calls:
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        # append the chatcompletion to the messages list
        messages.append(completion.choices[0].message)
        result = call_function(name, args)  
        # append the results of the tool call
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
        # log_messages(messages)
    

# call the model again with the results of the tool/function call added
completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    response_format=CustomerList
)

final_response = completion_2.choices[0].message.parsed
logger.info("-------")

if final_response:
    logger.info(type(final_response))
    for customer in final_response.customers:
        logger.info('Customer ID: %s, Company Name: %s, Contact Name: %s, Country: %s, Phone: %s',
                customer.customer_id, customer.company_name, customer.contact_name, customer.country, customer.phone)    
else: 
    logger.info("no customers found")

logger.info("-------")    

