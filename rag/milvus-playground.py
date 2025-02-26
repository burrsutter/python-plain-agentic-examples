from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

# https://www.youtube.com/watch?v=1rO5B9ArCKA



# Connect to Milvus Lite and store data in 'milvus_demo.db'
client = MilvusClient("./milvus_demo.db")


# Create a new collection with a specified dimension
client.create_collection(
    collection_name="demo_collection",
    dimension=384,  # Example dimension for the vector field
)


# Initialize the model, same one we use in private-docs demo
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



# Example data
docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
]

# Generate embeddings for the documents
embeddings = model.encode(docs, convert_to_list=True)


# Prepare data for insertion
data = [{"id": i, "vector": embeddings[i], "text": docs[i], "subject":"history"} for i in range(len(embeddings))]

# Insert data into the collection
client.insert(
    collection_name="demo_collection",
    data=data
)

res = client.search(
    collection_name="demo_collection",
    data=[embeddings[0]],
    filter="subject == 'history'",
    limit=2,
    output_fields=["text","subject"],
)

print(res)