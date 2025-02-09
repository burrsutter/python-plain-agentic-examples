import requests
from requests.auth import HTTPBasicAuth

# make sure to `pip install requests` 

# RabbitMQ API Credentials
RABBITMQ_HOST = "http://localhost:15672"
USERNAME = "guest"
PASSWORD = "guest"

def get_filtered_queues(prefix=None, contains=None):
    """Fetch and filter RabbitMQ queues by prefix or keyword."""
    url = f"{RABBITMQ_HOST}/api/queues"
    
    try:
        # Make API request
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response.raise_for_status()  # Raise error if request fails

        # Parse JSON response
        queues = response.json()
        queue_names = [queue["name"] for queue in queues]

        # Apply filters
        if prefix:
            queue_names = [q for q in queue_names if q.startswith(prefix)]
        if contains:
            queue_names = [q for q in queue_names if contains in q]

        return queue_names

    except requests.exceptions.RequestException as e:
        print(f"Error fetching queues: {e}")
        return []

# Example Usage
if __name__ == "__main__":
    prefix_filter = "my_"  # Change to filter by prefix
    contains_filter = "email"  # Change to filter by keyword

    queues_by_prefix = get_filtered_queues(prefix=prefix_filter)
    queues_by_keyword = get_filtered_queues(contains=contains_filter)

    print(f"Queues starting with '{prefix_filter}': {queues_by_prefix}")
    print(f"Queues containing '{contains_filter}': {queues_by_keyword}")