from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
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

# BERGS, ANTON,  BSBEV, BOTTM    
customer_id_to_find = "BERGS"
user_input = "Find customer " + customer_id_to_find + " details"


# this list serves as a memory bank, allowing for multiple LLM calls
messages = [
    {"role": "system", "content": "You are a helpful assistant that must use customer_search"},
    {"role": "user", "content": user_input}
]


class CustomerDetails(BaseModel):
    customer_id: str
    company_name: str
    contact_name: str
    country: str
    phone: str
    

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
    

tools = [
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
    if name == "customer_search_by_id":
        logger.info("calling customer_search_by_id")
        return customer_search_by_id(**args)


# for debugging what is in messages
def log_messages(messages):    
    logger.info(type(messages))  # identify type of object
    # for message in messages:
    #     # logger.info(message.model_dump_json(indent=4))
    #     logger.info(message)


# look inside the result for tool calls and make those tool calls

if completion.choices[0].message.tool_calls:
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)
        result = call_function(name, args)
        # logger.info(result)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
        log_messages(messages)
    
# call the model again with the results of the tool/function call added


completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    response_format=CustomerDetails
)

final_response = completion_2.choices[0].message.parsed
logger.info("-------")
# logger.info(final_response.customer_id)
# logger.info(final_response.company_name)
# logger.info(final_response.contact_name)
# logger.info(final_response.phone)

if final_response:
    logger.info(type(final_response))
    logging.info('Customer ID: %s, Company Name: %s, Contact Name: %s, Phone: %s',
                final_response.customer_id, final_response.company_name, final_response.contact_name, final_response.phone)    
else: 
    logger.info("no customers found")

logger.info("-------")    

