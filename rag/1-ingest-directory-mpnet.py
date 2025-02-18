import psycopg2
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
import textract
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

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

# Load Sentence Transformer model (all-mpnet-base-v2)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Create table to store documents and embeddings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS documentstwo (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding VECTOR(768)
    );
""")
conn.commit()

# Function to generate embeddings
def get_embedding(text):
    return model.encode(text, convert_to_numpy=True).tolist()  # Get embedding as a list

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

        # Generate embedding for each text chunk and store in PostgreSQL
        for chunk in chunks:
            embedding = get_embedding(chunk)
            cursor.execute(
                "INSERT INTO documentstwo (content, embedding) VALUES (%s, %s)",
                (chunk, embedding)
            )
    
conn.commit()

# Close the connection
cursor.close()
conn.close()