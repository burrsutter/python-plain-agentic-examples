from openai import OpenAI
import psycopg2
import numpy as np
from scipy.spatial.distance import cosine
from pgvector.psycopg2 import register_vector
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

print(os.getenv("INFERENCE_SERVER_URL"))
print(os.getenv("MODEL_NAME"))

DBNAME="rag_db"
DBUSER="postgres"
DBPASSWORD="admin"
DBHOST="localhost"
DBPORT="5432"

# User query
query = "first things first"

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DBNAME,
    user=DBUSER,
    password=DBPASSWORD,
    host=DBHOST,
    port=DBPORT
)

register_vector(conn)

cursor = conn.cursor()

# Load Sentence Transformer Model
os.environ["TOKENIZERS_PARALLELISM"] = "false"
embeddings = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed_query(text):
    return embeddings.encode(text, convert_to_numpy=True).tolist()  # Convert to list

def retrieve_info(query, k=2): # k is the number of results to return
    embedding = embed_query(query)
    try:
        cursor.execute("""
            SELECT content FROM documents 
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (embedding, k))  # Use the <-> operator for cosine similarity
        results = cursor.fetchall()
        return [Document(page_content=row[0]) for row in results]
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []



def generate_response(query):
    retrieved_docs = retrieve_info(query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),  # Use model from environment variable
        messages=[
            {"role": "system", "content": "You are an AI assistant that answers based on provided context. If the context doesn't contain the answer, say \"I don't know\""},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}\nAnswer:"}
        ],
        temperature=0  # Set temperature here
    )

    return response.choices[0].message.content.strip()

# 6. Putting it all together (same as before):
query = "What is Newton known for?"
response = generate_response(query)
print(query + " " + response)

query = "What did Stephen Hawking do?"  # Not in our knowledge base
response = generate_response(query)
print(query + " " + response)

# Close the database connection when finished
if conn:
    cursor.close()
    conn.close()
    print("Database connection closed.")
