import json
import os

# JSON_FILE = "output.json"  # The JSON file to read from
JSON_FILE = "invoice_2.json"  # The JSON file to read from

def find_gross_worth_data(json_file_path: str, target_column_name: str = "Gross worth"):
    """
    Parses a DoclingDocument JSON file, finds tables containing a specific
    column header, and extracts the data from that column.

    Args:
        json_file_path (str): The path to the input JSON file.
        target_column_name (str): The name of the column header to search for.

    Returns:
        dict: A dictionary where keys are table indices and values are lists
              of strings representing the data in the target column for that table.
              Returns an empty dict if the file doesn't exist, is not valid JSON,
              or the column is not found.
    """
    results = {}
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return results

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        return results
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return results

    tables = data.get('tables', [])
    if not tables:
        print("No tables found in the JSON data.")
        return results

    print(f"Found {len(tables)} table(s). Searching for column '{target_column_name}'...")

    for table_index, table in enumerate(tables):
        grid = table.get('data', {}).get('grid')
        if not grid or not isinstance(grid, list) or len(grid) < 1:
            print(f"Skipping table {table_index}: No valid grid data found.")
            continue

        header_row = grid[0]
        gross_worth_col_idx = None

        # Find the column index for the target header
        for col_idx, header_cell in enumerate(header_row):
            if isinstance(header_cell, dict) and header_cell.get('text') == target_column_name:
                gross_worth_col_idx = col_idx
                print(f"Found '{target_column_name}' header in table {table_index} at column index {gross_worth_col_idx}.")
                break

        # If header found, extract data from that column in subsequent rows
        if gross_worth_col_idx is not None:
            column_values = []
            # Start from the second row (index 1) as the first is the header
            for row_idx, data_row in enumerate(grid[1:], start=1):
                if isinstance(data_row, list) and len(data_row) > gross_worth_col_idx:
                    cell = data_row[gross_worth_col_idx]
                    if isinstance(cell, dict):
                        column_values.append(cell.get('text', '')) # Get text, default to empty string
                    else:
                         print(f"Warning: Unexpected cell format in table {table_index}, row {row_idx}, col {gross_worth_col_idx}: {cell}")
                else:
                    print(f"Warning: Row {row_idx} in table {table_index} does not have index {gross_worth_col_idx} or is not a list.")

            if column_values:
                results[table_index] = column_values
            else:
                print(f"Found header in table {table_index} but no data rows in that column.")
        # else:
            # print(f"'{target_column_name}' header not found in table {table_index}.")


    return results

if __name__ == "__main__":
    # Construct the path relative to the script's location
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, JSON_FILE)
    extracted_data = find_gross_worth_data(json_path)

    if not extracted_data:
        print(f"\nCould not find any data for the 'Gross worth' column in {json_path}.")
    else:
        print("\n--- Extracted 'Gross worth' Data ---")
        for table_idx, values in extracted_data.items():
            print(f"\nTable {table_idx}:")
            if not values:
                print("  (No values found in this column)")
            else:
                for i, value in enumerate(values):
                    print(f"  Row {i+1}: {value}") # +1 for 1-based row index (relative to data rows)
        print("------------------------------------")