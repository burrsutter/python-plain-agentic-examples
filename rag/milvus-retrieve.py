from pymilvus import MilvusClient
import numpy as np

# Connect to Milvus Lite and store data in 'milvus_demo.db'
client = MilvusClient("./milvus_demo.db")

# Use one of the inserted vectors as a query example
query_vector = vectors[0]

# Perform the search
results = client.search(
    collection_name="demo_collection",
    data=[query_vector],
    limit=2,  # Number of similar vectors to retrieve
    output_fields=["text"]  # Fields to include in the result
)

# Display the results
for hits in results:  # 'hits' is a list of dictionaries for each query vector
    for hit in hits:  # 'hit' is a dictionary for each matched entity
        print(f"ID: {hit['id']}, Text: {hit.get('text', 'N/A')}, Distance: {hit['distance']}")