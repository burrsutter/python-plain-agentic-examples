from duckduckgo_search import DDGS

# Create a DuckDuckGo search for leopard speed
with DDGS() as ddgs:
    results = ddgs.text("What is the top speed of a leopard in kilometers per hour?", max_results=5)

    # Print the search results
    for index, result in enumerate(results, start=1):
        title = result.get('title', 'No title')
        href = result.get('href', 'No URL')
        body = result.get('body', 'No description')
        print(f"{index}. {title} - {href}\n   {body}\n")

print("-" * 40)



