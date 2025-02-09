import pika

# Establish connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queue with priority argument (MUST match producer)
args = {"x-max-priority": 10}
channel.queue_declare(queue="priority_queue", arguments=args)

# Set prefetch count to 1 (Consumer processes 1 message at a time)
channel.basic_qos(prefetch_count=1)

# Define callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()} with priority {properties.priority}")

    # Simulate processing time
    import time
    time.sleep(1)

    # Acknowledge message AFTER processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming (Manual acknowledgment)
channel.basic_consume(queue="priority_queue", on_message_callback=callback, auto_ack=False)

print(" [*] Waiting for messages in priority order. To exit, press CTRL+C")
channel.start_consuming()