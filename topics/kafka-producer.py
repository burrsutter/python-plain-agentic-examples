from kafka import KafkaProducer

# Kafka broker address
KAFKA_BROKER = "localhost:9092"

# Kafka topic to send messages to
TOPIC_NAME = "test_topic"

# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

# Send messages
# messages = ["hello", "world", "this", "is", "Kafka!"]
messages = ["stuff", "happens", "daily"]
# messages = ["Aa", "Bb", "Cc"]

for msg in messages:
    producer.send(TOPIC_NAME, msg.encode("utf-8"))
    print(f"Sent: {msg}")

# Ensure all messages are sent before exiting
producer.flush()
producer.close()