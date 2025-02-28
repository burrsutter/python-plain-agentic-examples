#!/usr/bin/env python3
"""
Test script to publish messages to a RabbitMQ queue.
This is useful for testing the queue-server application.
"""

import argparse
import json
import os
import random
import time
import pika

# Parse command line arguments
parser = argparse.ArgumentParser(description='Publish test messages to a RabbitMQ queue')
parser.add_argument('--host', default='localhost', help='RabbitMQ host (default: localhost)')
parser.add_argument('--port', type=int, default=5672, help='RabbitMQ port (default: 5672)')
parser.add_argument('--user', default='guest', help='RabbitMQ username (default: guest)')
parser.add_argument('--password', default='guest', help='RabbitMQ password (default: guest)')
parser.add_argument('--vhost', default='/', help='RabbitMQ virtual host (default: /)')
parser.add_argument('--queue', required=True, help='Queue name to publish to')
parser.add_argument('--count', type=int, default=10, help='Number of messages to publish (default: 10)')
parser.add_argument('--interval', type=float, default=1.0, help='Interval between messages in seconds (default: 1.0)')
parser.add_argument('--json', action='store_true', help='Publish JSON messages (default: text)')
args = parser.parse_args()

# Connect to RabbitMQ
credentials = pika.PlainCredentials(args.user, args.password)
parameters = pika.ConnectionParameters(
    host=args.host,
    port=args.port,
    virtual_host=args.vhost,
    credentials=credentials
)

print(f"Connecting to RabbitMQ at {args.host}:{args.port}...")
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=args.queue, durable=True)

# Sample data for JSON messages
sample_products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
    {"id": 2, "name": "Smartphone", "price": 699.99, "category": "Electronics"},
    {"id": 3, "name": "Headphones", "price": 149.99, "category": "Audio"},
    {"id": 4, "name": "Coffee Maker", "price": 89.99, "category": "Kitchen"},
    {"id": 5, "name": "Running Shoes", "price": 129.99, "category": "Sports"}
]

sample_users = [
    {"id": 101, "name": "Alice Smith", "email": "alice@example.com"},
    {"id": 102, "name": "Bob Johnson", "email": "bob@example.com"},
    {"id": 103, "name": "Charlie Brown", "email": "charlie@example.com"},
    {"id": 104, "name": "Diana Miller", "email": "diana@example.com"}
]

sample_events = ["login", "logout", "purchase", "view_item", "add_to_cart", "remove_from_cart", "checkout"]

# Publish messages
print(f"Publishing {args.count} messages to queue '{args.queue}' with {args.interval}s interval...")

for i in range(args.count):
    if args.json:
        # Create a random JSON message
        event_type = random.choice(sample_events)
        timestamp = time.time()
        
        if event_type in ["purchase", "view_item", "add_to_cart", "remove_from_cart"]:
            product = random.choice(sample_products)
            user = random.choice(sample_users)
            message = {
                "event": event_type,
                "timestamp": timestamp,
                "user": user,
                "product": product,
                "session_id": f"sess_{random.randint(10000, 99999)}"
            }
        else:
            user = random.choice(sample_users)
            message = {
                "event": event_type,
                "timestamp": timestamp,
                "user": user,
                "session_id": f"sess_{random.randint(10000, 99999)}"
            }
        
        body = json.dumps(message)
    else:
        # Create a simple text message
        body = f"Test message #{i+1} sent at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=args.queue,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    
    print(f"Published message {i+1}/{args.count}")
    
    # Wait for the specified interval
    if i < args.count - 1:  # Don't wait after the last message
        time.sleep(args.interval)

# Close the connection
connection.close()
print(f"Done! Published {args.count} messages to queue '{args.queue}'")
print("You can now use the queue-server application to monitor or peek at these messages.")
