import json
import os

def extract_table_columns(json_file_path: str, target_column_names: list[str]):
    """
    Parses a DoclingDocument JSON file, finds tables containing specified
    column headers, and extracts the data from those columns for each row.

    Args:
        json_file_path (str): The path to the input JSON file.
        target_column_names (list[str]): A list of column header names to extract.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a row
                    containing the data for the target columns from all relevant tables.
                    Returns an empty list if the file doesn't exist, is not valid JSON,
                    or the required columns are not found in any table.
    """
    all_extracted_rows = []
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return all_extracted_rows

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        return all_extracted_rows
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return all_extracted_rows

    tables = data.get('tables', [])
    if not tables:
        print("No tables found in the JSON data.")
        return all_extracted_rows

    print(f"Found {len(tables)} table(s). Searching for columns: {', '.join(target_column_names)}...")

    for table_index, table in enumerate(tables):
        grid = table.get('data', {}).get('grid')
        if not grid or not isinstance(grid, list) or len(grid) < 1:
            print(f"Skipping table {table_index}: No valid grid data found.")
            continue

        header_row = grid[0]
        column_indices = {} # Dictionary to store {column_name: index}

        # Find the column indices for all target headers
        for col_idx, header_cell in enumerate(header_row):
            if isinstance(header_cell, dict):
                header_text = header_cell.get('text')
                if header_text in target_column_names:
                    column_indices[header_text] = col_idx
                    print(f"Found '{header_text}' header in table {table_index} at column index {col_idx}.")

        # Check if all target columns were found in this table's header
        if len(column_indices) == len(target_column_names):
            print(f"Found all target columns in table {table_index}. Extracting data...")
            table_rows = []
            # Start from the second row (index 1) as the first is the header
            for row_idx, data_row in enumerate(grid[1:], start=1):
                row_data = {}
                valid_row = True
                for col_name, col_idx in column_indices.items():
                    if isinstance(data_row, list) and len(data_row) > col_idx:
                        cell = data_row[col_idx]
                        if isinstance(cell, dict):
                            row_data[col_name] = cell.get('text', '') # Get text, default to empty string
                        else:
                            print(f"Warning: Unexpected cell format in table {table_index}, row {row_idx}, col {col_idx}: {cell}")
                            row_data[col_name] = None # Or some indicator of missing data
                            valid_row = False # Or decide how to handle partial rows
                    else:
                        print(f"Warning: Row {row_idx} in table {table_index} does not have index {col_idx} or is not a list.")
                        row_data[col_name] = None
                        valid_row = False # Or decide how to handle partial rows
                        break # Stop processing this row if a column is missing

                if valid_row and row_data: # Only add if row was processed correctly and has data
                     table_rows.append(row_data)

            if table_rows:
                print(f"Extracted {len(table_rows)} rows from table {table_index}.")
                all_extracted_rows.extend(table_rows) # Add rows from this table to the main list
            else:
                print(f"Found headers in table {table_index} but no valid data rows extracted.")
        else:
            missing_cols = set(target_column_names) - set(column_indices.keys())
            if missing_cols:
                 print(f"Skipping table {table_index}: Did not find all target columns. Missing: {', '.join(missing_cols)}")


    return all_extracted_rows

if __name__ == "__main__":
    # Construct the path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Use abspath for reliability
    input_json_path = os.path.join(script_dir, "output.json")
    output_json_path = os.path.join(script_dir, "extracted_data.json")
    columns_to_extract = ["Description", "Gross worth"]

    extracted_rows = extract_table_columns(input_json_path, columns_to_extract)

    if not extracted_rows:
        print(f"\nCould not find any data for the specified columns in {input_json_path}.")
    else:
        print(f"\n--- Extracted {len(extracted_rows)} total rows ---")
        # Save the extracted data to a new JSON file
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f_out:
                json.dump(extracted_rows, f_out, indent=2, ensure_ascii=False)
            print(f"Successfully saved extracted data to {output_json_path}")
        except Exception as e:
            print(f"Error saving extracted data to {output_json_path}: {e}")

        # Optionally print a sample of the data
        print("\nSample of extracted data:")
        for i, row in enumerate(extracted_rows[:5]): # Print first 5 rows
             print(f" Row {i+1}: {row}")
        if len(extracted_rows) > 5:
            print(" ... (more rows in the output file)")
        print("------------------------------------")