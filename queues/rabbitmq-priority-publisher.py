import pika

# Establish connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Publish messages with different priorities
channel.basic_publish(
    exchange="",
    routing_key="priority_queue",
    body="Low priority message",
    properties=pika.BasicProperties(priority=1)  # Low priority
)

channel.basic_publish(
    exchange="",
    routing_key="priority_queue",
    body="High priority message",
    properties=pika.BasicProperties(priority=10)  # High priority
)

channel.basic_publish(
    exchange="",
    routing_key="priority_queue",
    body="Medium priority message",
    properties=pika.BasicProperties(priority=5)  # Medium priority
)

channel.basic_publish(
    exchange="",
    routing_key="priority_queue",
    body="Another high priority message",
    properties=pika.BasicProperties(priority=10)  # High priority
)


print(" [x] Sent messages with different priorities.")

connection.close()