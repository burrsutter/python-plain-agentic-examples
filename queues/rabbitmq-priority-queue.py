import pika

# Establish connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue with priority enabled (max priority 10)
args = {"x-max-priority": 10}
channel.queue_declare(queue="priority_queue", arguments=args)

print(" [*] Priority queue declared.")
connection.close()