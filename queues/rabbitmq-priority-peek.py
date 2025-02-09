import pika

def peek_priority_queue(queue_name="priority_queue", host="localhost"):
    """Peek at all messages in a RabbitMQ priority queue without consuming them."""
    
    # Establish connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    # Get queue stats (message count)
    queue = channel.queue_declare(queue=queue_name, passive=True)
    message_count = queue.method.message_count
    print(f"\n [*] Queue '{queue_name}' has {message_count} messages.")

    # Peek at all messages without consuming
    print("\n [*] Peeking at messages (without consuming):")
    
    messages = []
    while True:
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=False)
        if method_frame:
            priority = header_frame.priority if header_frame else 0  # Default to 0 if no priority
            messages.append((priority, body.decode()))
        else:
            break  # Stop when no more messages are available

    if messages:
        # Sort messages by priority (higher priority first)
        messages.sort(reverse=True, key=lambda x: x[0])

        for i, (priority, msg) in enumerate(messages, 1):
            print(f" [x] Message {i}: {msg} (Priority: {priority})")
    else:
        print(" [x] No messages found in the queue.")

    # Close connection
    connection.close()

    return {"queue_name": queue_name, "message_count": message_count, "messages": messages}

# Example Usage
if __name__ == "__main__":
    peek_priority_queue()