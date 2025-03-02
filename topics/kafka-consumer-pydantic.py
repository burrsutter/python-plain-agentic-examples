from kafka import KafkaConsumer
from message import Message

# Kafka configuration
KAFKA_BROKER = "localhost:9092"  # Change if your broker is on another host
TOPIC_NAME = "test_topic"  # Replace with your topic name

# Create Kafka consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset="earliest",  # Start from the earliest message
    enable_auto_commit=True,  # Automatically commit offsets
    #group_id="simple_consumer_group"
)

print(f"Listening for messages on topic: {TOPIC_NAME}")

# Consume messages
for kafka_message in consumer:
    print(f"Received: {kafka_message.value.decode('utf-8')}")