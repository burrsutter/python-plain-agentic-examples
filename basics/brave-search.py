from brave import Brave # pip install brave-search
import os
from dotenv import load_dotenv
load_dotenv()

BRAVE_API_KEY=os.getenv("BRAVE_API_KEY")

# Initialize the Brave Search client with your API key
brave = Brave(BRAVE_API_KEY)

# # Define your search query and the number of results you want
# query = "What is the top speed of a leopard in kilometers per hour?"
# num_results = 5

# # Perform the search
# search_results = brave.search(q=query, count=num_results)

# # Access web, news, and video results
# web_results = search_results.web_results
# # news_results = search_results.news_results
# # video_results = search_results.video_results

# # Print web results
# for index, result in enumerate(web_results, start=1):
#     print(f"{index}. {result['title']} - {result['url']}")
#     print(f"   {result['description']}\n")

print("-" * 40)

# Define your search query and the number of results you want
query = "Pont des Arts length in meters"
num_results = 5

# Perform the search
search_results = brave.search(q=query, count=num_results)

# Access web, news, and video results
web_results = search_results.web_results
# news_results = search_results.news_results
# video_results = search_results.video_results

# Print web results
for index, result in enumerate(web_results, start=1):
    print(f"{index}. {result['title']} - {result['url']}")
    print(f"   {result['description']}\n")

