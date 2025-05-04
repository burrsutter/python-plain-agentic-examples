import json
import os

JSON_FILE = "output.json"  # The JSON file to read from

def find_element_by_ref(data: dict, ref: str):
    """Finds an element in the JSON data using its $ref."""
    if not ref or not ref.startswith('#/'):
        return None
    parts = ref[2:].split('/')
    if len(parts) != 2:
        return None
    element_type, index_str = parts
    try:
        index = int(index_str)
        if element_type in data and isinstance(data[element_type], list) and 0 <= index < len(data[element_type]):
            return data[element_type][index]
    except ValueError:
        return None
    return None

def extract_seller_info(json_file_path: str):
    """
    Parses a DoclingDocument JSON file and extracts the seller information.

    Args:
        json_file_path (str): The path to the input JSON file.

    Returns:
        str: The extracted seller information text, or None if not found.
    """
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return None

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return None

    body_children = data.get('body', {}).get('children', [])
    texts = data.get('texts', [])
    seller_header_ref = None
    seller_info = None

    # 1. Find the reference to the "Seller:" header text element
    for text_element in texts:
        if text_element.get('text') == "Seller:" and text_element.get('label') == "section_header":
            seller_header_ref = text_element.get('self_ref')
            print(f"Found 'Seller:' header element with ref: {seller_header_ref}")
            break

    if not seller_header_ref:
        print("Could not find the 'Seller:' header text element.")
        # Alternative strategy: Look for text containing seller address patterns? (More complex)
        return None

    # 2. Find the header ref in the body children to determine the next element
    try:
        header_index_in_body = -1
        for i, child in enumerate(body_children):
            if child.get('$ref') == seller_header_ref:
                header_index_in_body = i
                break

        if header_index_in_body == -1 or header_index_in_body + 1 >= len(body_children):
            print(f"Could not find the element following the seller header in body children.")
            return None

        # 3. Get the reference to the element immediately following the header
        seller_info_ref = body_children[header_index_in_body + 1].get('$ref')
        print(f"Reference to element following seller header: {seller_info_ref}")

        if not seller_info_ref:
             print(f"Invalid reference found after seller header.")
             return None

        # 4. Find the actual seller info element using its reference
        seller_info_element = find_element_by_ref(data, seller_info_ref)

        if seller_info_element and 'text' in seller_info_element:
            seller_info = seller_info_element['text']
            print("Successfully extracted seller information.")
        else:
            print(f"Could not find or extract text from the seller info element ({seller_info_ref}).")
            # Maybe the structure is different? Check if the element is a group?
            if seller_info_element and seller_info_element.get('name') == 'group':
                 print("Seller info element is a group. Trying to extract text from its children...")
                 # Add logic here to extract text from children if needed
                 pass


    except Exception as e:
        print(f"An error occurred while processing body children or references: {e}")
        return None


    return seller_info

if __name__ == "__main__":
    # Construct the path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, JSON_FILE)

    print(f"Attempting to extract seller info from: {json_path}")
    seller_details = extract_seller_info(json_path)

    if seller_details:
        print("\n--- Extracted Seller Information ---")
        print(seller_details)
        print("------------------------------------")
    else:
        print("\nFailed to extract seller information.")