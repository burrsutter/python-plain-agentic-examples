from kafka import KafkaProducer
import json

# Kafka broker address
KAFKA_BROKER = "localhost:9092"

# Kafka topic to send messages to
TOPIC_NAME = "test_topic"

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Serialize messages as JSON
)

# JSON message to send as a single message
message = [{
    "message": "Hello, World!"
}]

# Send the JSON object as one message
producer.send(TOPIC_NAME, message)
print(f"Sent: {message}")

# Ensure all messages are sent before exiting
producer.flush()
producer.close()