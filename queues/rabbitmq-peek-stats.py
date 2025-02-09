import pika

queue_name = "my_queue"

def peek_queue(queue_name=queue_name, host='localhost'):
    """Peek at all messages in a RabbitMQ queue and display queue stats without consuming them."""
    
    # Establish connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    # Get queue stats
    queue = channel.queue_declare(queue=queue_name, passive=True)
    message_count = queue.method.message_count
    print(f"\n [*] Queue '{queue_name}' has {message_count} messages.")

    # Peek at all messages without consuming them
    print("\n [*] Peeking at messages in queue:")

    messages = []
    while True:
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=False)
        if method_frame:
            messages.append(body.decode())
        else:
            break

    if messages:
        for i, msg in enumerate(messages, 1):
            print(f" [x] Message {i}: {msg}")
    else:
        print(" [x] No messages found in the queue.")

    # Close connection
    connection.close()
    return {"queue_name": queue_name, "message_count": message_count, "messages": messages}

# Example Usage
if __name__ == "__main__":
    result = peek_queue()