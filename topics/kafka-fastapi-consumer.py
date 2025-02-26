from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

KAFKA_TOPIC = "test_topic"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"


origins = [
    "*",  # If your frontend is running on this origin    
]

# Add the CORSMiddleware to the FastAPI application.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,  # Allows cookies and other credentials to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def main():
    return {"message": "SSE streamer at /sse"}



async def consume_kafka():
    """ Async generator that consumes messages from Kafka """
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        #enable_auto_commit=True,
        #group_id="sse-consumer-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            decoded_message = msg.value.decode("utf-8")
            print(f"Received from Kafka: {decoded_message}")  # Debugging
            yield {"data": json.dumps({"message": decoded_message})}
    finally:
        await consumer.stop()

@app.get("/sse")
async def sse_stream():
    return EventSourceResponse(consume_kafka())