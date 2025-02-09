from duckduckgo_search import DDGS

# Create a DuckDuckGo search for leopard speed
with DDGS() as ddgs:
    results = ddgs.text("What is the top speed of a leopard in kilometers per hour?", max_results=5)

# Print the search results
for index, result in enumerate(results, start=1):
    print(f"{index}. {result['title']} - {result['href']}")

print("-" * 40)

# Create a DuckDuckGo search for lenth of Pont des Arts
with DDGS() as ddgs:
    results = ddgs.text("What length of the Pont des Arts in meters?", max_results=5)

# Print the search results
for index, result in enumerate(results, start=1):
    print(f"{index}. {result['title']} - {result['href']}")


