import pika

# --------------------------------------------------------------
# Basic connection, queue connection, message publish
# --------------------------------------------------------------

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

queue_name = "my_queue"

# Declare the queue (auto-creates if needed)
channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='',
                      routing_key=queue_name,
                      body='Hello RabbitMQ!')

print(" [x] Sent 'Hello, RabbitMQ!'")

connection.close()

