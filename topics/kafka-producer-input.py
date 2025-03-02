from kafka import KafkaProducer
from dotenv import load_dotenv
from message import Message
import json
import os
import uuid
from datetime import datetime

# Load env vars
load_dotenv()
KAFKA_INPUT_TOPIC=os.getenv("KAFKA_INPUT_TOPIC") 
KAFKA_BROKER=os.getenv("KAFKA_BROKER")

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER    
)

message = Message(
    id=str(uuid.uuid4()),
    timestamp=datetime.utcnow().isoformat(), 
    content="Body of Message"
)

# Send the JSON object as one message
value = message.model_dump_json().encode('utf-8')

print(f"To Be Sent: {value}")

producer.send(KAFKA_INPUT_TOPIC, value)

print(f"Sent: {message}")

# Ensure all messages are sent before exiting
producer.flush()
producer.close()

