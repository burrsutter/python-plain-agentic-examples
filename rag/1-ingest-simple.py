import psycopg2
import numpy as np
from openai import OpenAI

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

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

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DBNAME,
    user=DBUSER,
    password=DBPASSWORD,
    host=DBHOST,
    port=DBPORT
)

try:
    cursor = conn.cursor()

    # Create table to store documents and embeddings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding VECTOR(768)
        );
    """)
    conn.commit()
except Exception as e:
    print(f"Error connecting to or setting up database: {e}")
    exit()  # Exit if database setup fails        

os.environ["TOKENIZERS_PARALLELISM"] = "false"
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


knowledge_base = {
    "Albert Einstein": "Developed the theory of relativity. Famous for E=mc².",
    "Marie Curie": "Pioneered research on radioactivity. First woman to win a Nobel Prize.",
    "Isaac Newton": "Formulated the laws of motion and universal gravitation.",
    "Charles Darwin": "Developed the theory of evolution by natural selection."
}

# Function to Generate Embeddings
def get_embedding(text):
    return model.encode(text, convert_to_numpy=True).tolist()  # Convert to list


# Insert documents and their embeddings into the database with pgvector extension
try:
    for name, info in knowledge_base.items():
        text = f"{name}: {info}"
        embedding = get_embedding(text)  # Get the embedding vector

        cursor.execute("INSERT INTO documents (content, embedding) VALUES (%s, %s)", (text, embedding))

    conn.commit()
    print("Documents inserted successfully.")
except Exception as e:
    print(f"Error inserting documents: {e}")
    conn.rollback()  # Rollback in case of error    

# Close the connection
cursor.close()
conn.close()