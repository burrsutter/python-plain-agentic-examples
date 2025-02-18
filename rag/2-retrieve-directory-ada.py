from openai import OpenAI
import psycopg2
import numpy as np
from scipy.spatial.distance import cosine
from pgvector.psycopg2 import register_vector

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
query = "what is the mad hatter's riddle"
# query = "What happened when Alice followed the rabbit?"
# query = "where is Tweedledee?"

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

# Function to generate query embedding
def get_query_embedding(query):
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# Function to retrieve relevant documents
def retrieve_documents(query, top_k=3):
    query_embedding = get_query_embedding(query)
    
    # Perform similarity search in PostgreSQL using pgvector
    cursor.execute("""
        SELECT content FROM documentsone
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """, (query_embedding.tolist(), top_k))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in results]

retrieved_docs = retrieve_documents(query)

context = "\n\n".join(retrieved_docs)

def generate_response(query, context, max_chars=4000):
    truncated_context = context[:max_chars] 
    prompt = f"""You are an AI that answers questions using the given context.
If the context does not contain an answer, respond with \"I don't know\".

Context:
{truncated_context}

Question: {query}
Answer:"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),  
        messages=[{"role": "system", "content": "You are an AI assistant answering based on provided context."},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# Display retrieved chunks
print("\n🔍 Top Retrieved Chunks:\n")
for idx, doc in enumerate(retrieved_docs, 1):
    chunk_length = len(doc) 
    print(f"{idx}. ({chunk_length} characters) {doc[:500]}...\n")  # first 500 characters



# Get LLM-generated response
llm_response = generate_response(query, context)
print("\n💡 AI Response:\n", llm_response)

# Close the connection
cursor.close()
conn.close()




