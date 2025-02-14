from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import psycopg2
from psycopg2 import sql

import os
import json


load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

user_input = "What are customer BSBEV's details?"

messages = [
    {"role": "system", "content": "You are a helpful assistant that must customer_search tool"},
    {"role": "user", "content": user_input}
]



class CustomerDetails(BaseModel):
    customer_id: str
    company_name: str
    contact_name: str
    country: str
    phone: str
    

def customer_search(customer_id):
    """ this is mock data """
    print("customer_search " + customer_id)

    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(
            dbname="northwind",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute a query to retrieve the desired customer        
        query = sql.SQL("SELECT customer_id, company_name, contact_name, phone FROM {table} WHERE {id_field} = %s").format(
            table=sql.Identifier('customer'),
            id_field=sql.Identifier('customer_id')
        )

        cursor.execute(query)

        # Fetch all customer records
        customers = cursor.fetchone()

        # Display the list of customers
        print("found customer")
        for customer in customers:
            print(customer)

    except Exception as error:
            print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        # Close the cursor and connection to clean up
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return "Customer " + customer_id + " is ACME Corporation"


tools = [
    {
        "type" : "function",
        "function" : {
            "name": "customer_search",
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
    }
]

# Make the request, passing in the tools defintion

completion = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),    
    messages=messages,
    tools=tools,
)

completion.model_dump()

# the callback

def call_function(name, args):
    if name == "fetch_customer_details":
        print("calling fetch_customer_details")
        return fetch_customer_details(**args)

# for debugging

def print_messages(messages):
    print("!!!!!")
    print(type(messages))  # identify type of object
    # print(json.dumps(messages)) # convert to JSON 
    print(messages)
    print("!!!!!")


# look inside the result for tool calls and make those tool calls

for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)
    result = call_function(name, args)
    print_messages(result)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )
    print_messages(messages)
    
# call the model again with the results of the tool/function call added

class CustomerDetails(BaseModel):
    customer_id: str
    customer_name: str
    balance: float


completion_2 = client.beta.chat.completions.parse(
    model=os.getenv("MODEL_NAME"),
    messages=messages,
    tools=tools,
    response_format=CustomerDetails
)

final_response = completion_2.choices[0].message.parsed
print("-------")
print(final_response.customer_id)
print(final_response.customer_name)
print(final_response.balance)


