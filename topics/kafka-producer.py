from kafka import KafkaProducer

# Kafka broker address
KAFKA_BROKER = "localhost:9092"

# Kafka topic to send messages to
# TOPIC_NAME = "test_topic"
TOPIC_NAME = "in-gpt4o"

# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

# Send messages
# messages = ["hello", "world", "this", "is", "Kafka!"]
# messages = ["stuff", "happens", "daily"]
messages = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]
# messages = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"]


for msg in messages:
    producer.send(TOPIC_NAME, msg.encode("utf-8"))
    print(f"Sent: {msg}")

# Ensure all messages are sent before exiting
producer.flush()
producer.close()