#!/usr/bin/env python3
"""
Sample Kafka producer to generate test messages for the Kafka Peeker SSE application.
"""

import json
import time
import random
import argparse
import logging
from datetime import datetime
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Sample message types and their templates
MESSAGE_TEMPLATES = {
    "user": {
        "type": "user",
        "id": lambda: random.randint(1000, 9999),
        "username": lambda: random.choice(["alice", "bob", "charlie", "dave", "eve"]),
        "email": lambda username: f"{username}@example.com",
        "status": lambda: random.choice(["active", "inactive", "pending"]),
        "created_at": lambda: datetime.now().isoformat(),
    },
    "order": {
        "type": "order",
        "id": lambda: f"ORD-{random.randint(10000, 99999)}",
        "user_id": lambda: random.randint(1000, 9999),
        "items": lambda: random.randint(1, 10),
        "total": lambda: round(random.uniform(10.0, 500.0), 2),
        "status": lambda: random.choice(["pending", "processing", "shipped", "delivered"]),
        "created_at": lambda: datetime.now().isoformat(),
    },
    "notification": {
        "type": "notification",
        "id": lambda: f"NOTIF-{random.randint(10000, 99999)}",
        "user_id": lambda: random.randint(1000, 9999),
        "message": lambda: random.choice([
            "Your order has been shipped!",
            "New login detected on your account",
            "Password reset requested",
            "Your subscription is about to expire",
            "New feature available!",
        ]),
        "priority": lambda: random.choice(["low", "medium", "high"]),
        "read": lambda: random.choice([True, False]),
        "created_at": lambda: datetime.now().isoformat(),
    },
    "event": {
        "type": "event",
        "id": lambda: f"EVT-{random.randint(10000, 99999)}",
        "name": lambda: random.choice([
            "user_login", 
            "user_logout", 
            "page_view", 
            "button_click", 
            "form_submit"
        ]),
        "source": lambda: random.choice(["web", "mobile", "api"]),
        "user_id": lambda: random.randint(1000, 9999),
        "metadata": lambda: {
            "ip": f"192.168.1.{random.randint(1, 255)}",
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
                "Mozilla/5.0 (Linux; Android 11; SM-G998B)"
            ])
        },
        "created_at": lambda: datetime.now().isoformat(),
    }
}

def generate_message(message_type=None):
    """Generate a random message based on templates"""
    if message_type is None or message_type not in MESSAGE_TEMPLATES:
        message_type = random.choice(list(MESSAGE_TEMPLATES.keys()))
    
    template = MESSAGE_TEMPLATES[message_type]
    message = {}
    
    # Process each field in the template
    for key, value_generator in template.items():
        if callable(value_generator):
            # If the value is a function, call it to generate a value
            if key == "email" and "username" in message:
                # Special case for email which depends on username
                message[key] = value_generator(message["username"])
            else:
                message[key] = value_generator()
        else:
            # Static value
            message[key] = value_generator
    
    return message

def produce_messages(broker, topic, interval, count, message_types=None):
    """Produce messages to a Kafka topic"""
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=broker,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    logger.info(f"Connected to Kafka broker: {broker}")
    logger.info(f"Producing messages to topic: {topic}")
    
    try:
        for i in range(count):
            # Generate message
            if message_types:
                message_type = random.choice(message_types)
            else:
                message_type = None
            
            message = generate_message(message_type)
            
            # Send message to Kafka
            producer.send(topic, message)
            logger.info(f"Produced message {i+1}/{count}: {message}")
            
            # Wait for the specified interval
            if i < count - 1:  # Don't sleep after the last message
                time.sleep(interval)
        
        # Ensure all messages are sent
        producer.flush()
        logger.info(f"Successfully produced {count} messages")
    
    except Exception as e:
        logger.error(f"Error producing messages: {e}")
    
    finally:
        producer.close()
        logger.info("Producer closed")

def main():
    """Main function to parse arguments and start producing messages"""
    parser = argparse.ArgumentParser(description="Kafka message producer for testing")
    parser.add_argument("--broker", default="localhost:9092", help="Kafka broker address")
    parser.add_argument("--topic", default="test_topic", help="Kafka topic to produce to")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between messages in seconds")
    parser.add_argument("--count", type=int, default=10, help="Number of messages to produce")
    parser.add_argument("--types", nargs="+", choices=list(MESSAGE_TEMPLATES.keys()), 
                        help="Message types to produce (random if not specified)")
    
    args = parser.parse_args()
    
    produce_messages(args.broker, args.topic, args.interval, args.count, args.types)

if __name__ == "__main__":
    main()
