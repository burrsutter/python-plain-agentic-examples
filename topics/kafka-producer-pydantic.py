from kafka import KafkaProducer
from message import Message # Pydantic class defined in message.py
import os
import uuid
from datetime import datetime


# Kafka configuration
KAFKA_BROKER = "localhost:9092"  # Change if your broker is on another host
TOPIC_NAME = "test_topic"  # Replace with your topic name

# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

kafka_message = Message(
    id=str(uuid.uuid4()),
    timestamp=datetime.utcnow().isoformat(), 
    content="Body of Message"
)


# Send the JSON object as one message
value = kafka_message.model_dump_json().encode('utf-8')

print(f"To Be Sent: {value}")

producer.send(TOPIC_NAME, value)

# Ensure all messages are sent before exiting
producer.flush()
producer.close()

