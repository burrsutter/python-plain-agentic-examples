import pika

# --------------------------------------------------------------
# Basic connection, queue connection, message consumer
# --------------------------------------------------------------

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

queue_name = "my_queue"

# Declare the queue (auto-creates if needed)
channel.queue_declare(queue=queue_name)

# Define callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

# Consume messages
channel.basic_consume(queue=queue_name,
                      on_message_callback=callback,
                      auto_ack=True) # eaten

print(' [*] Waiting for messages. To exit, press CTRL+C')

channel.start_consuming()

connection.close()
