import psycopg2
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
import textract
from langchain.text_splitter import RecursiveCharacterTextSplitter


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

cursor = conn.cursor()

# Create table to store documents and embeddings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS documentsone (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding VECTOR(1536)
    );
""")
conn.commit()

# Function to generate embeddings
def get_embedding(text):
    response = client.embeddings.create(        
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

# Directory containing the documents
directory_path = './documents'

# Iterate over all files in the directory
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    if os.path.isfile(file_path):
        # Extract text from the document
        text = textract.process(file_path).decode('utf-8')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        # Generate embedding for the text
        for chunk in chunks:
            embedding = get_embedding(chunk)            
            embedding_array = np.array(embedding, dtype=np.float32)
            embedding_list = embedding_array.tolist()
            # Insert document content and embedding into the database
            cursor.execute(
                "INSERT INTO documentsone (content, embedding) VALUES (%s, %s)",
                (text, embedding_list)
            )
    
conn.commit()

# Close the connection
cursor.close()
conn.close()