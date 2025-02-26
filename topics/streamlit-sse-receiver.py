import streamlit as st
import sseclient
import requests
import pandas as pd
import time

# Set SSE URL 
SSE_URL = "http://localhost:8000/sse"  # Example SSE server URL

st.title("📡 Real-time SSE Events Viewer")

# Placeholder for dynamic updates
table_placeholder = st.empty()

# Data storage for the table
data = []

# Function to listen to SSE stream
def get_sse_events(url):
    response = requests.get(url, stream=True)
    client = sseclient.SSEClient(response)
    for event in client.events():
        yield event.data

# Maximum number of events to display
ROLLING_WINDOW = 20

# Start listening for events
with st.spinner("Listening for SSE events..."):
    for event_data in get_sse_events(SSE_URL):
        event_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"Event: {event_data}")
        # Add new event to the list
        data.append({"Timestamp": event_time, "Event": event_data})
        
        # Keep only the last 20 events (rolling window)
        if len(data) > ROLLING_WINDOW:
            data.pop(0)  # Remove the oldest event
        
        # Convert list to DataFrame
        df = pd.DataFrame(data)
        
        # Display as a table
        table_placeholder.dataframe(df)
