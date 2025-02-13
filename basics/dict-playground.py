
duckduckgo_result="[{'title': 'How Fast Are Leopards? Top Speeds and How It Compares ... - AZ Animals', 'href': 'https://a-z-animals.com/blog/how-fast-leopards-top-speeds-how-compares-other-big-cats/', 'body': 'Cats of all sizes are known for their stealth, agility, and speed. We all know cheetahs take the cake when it comes to their record-breaking speed. But what about leopards? They are quick climbers, sneaky hunters, and pretty fast on land, but just how fast? Leopards can run up to speeds of 36 miles per hour.'}]"

print("Type:", type(duckduckgo_result))

duckduckgo_result_dict = eval(duckduckgo_result)

# Extract 'body' from each dictionary
for item in duckduckgo_result_dict:
    print(item["body"])