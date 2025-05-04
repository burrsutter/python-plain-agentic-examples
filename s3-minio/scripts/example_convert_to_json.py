import json
from docling.document_converter import DocumentConverter, ConversionStatus

# --- Configuration ---
# Replace with the actual path to your PDF file or a URL
pdf_source = "../invoices/invoice_2.pdf"

# Output JSON file path (optional)
output_json_file = "output.json"

# --- Conversion ---
try:
    # 1. Initialize the converter
    converter = DocumentConverter()

    # 2. Convert the PDF document
    #    Set raises_on_error=False to get status/errors instead of exceptions
    print(f"Converting '{pdf_source}'...")
    result = converter.convert(pdf_source, raises_on_error=True)

    # 3. Check conversion status
    if result.status in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS):
        print("Conversion successful.")

        # 4. Access the DoclingDocument object
        docling_doc = result.document

        # 5. Export the document to JSON
        #    The export_to_json method returns a dictionary representing the document
        json_data = docling_doc.export_to_dict()

        # 6. Print the JSON (optional)
        #    Use json.dumps for pretty printing
        print("\n--- JSON Output (pretty-printed sample) ---")
        print(json.dumps(json_data, indent=2)[:1000] + "\n...") # Print first 1000 chars

        # 7. Save the JSON to a file (optional)
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"\nFull JSON saved to '{output_json_file}'")

    else:
        print(f"Conversion failed with status: {result.status}")
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"- {error.component_type}: {error.error_message}")

except Exception as e:
    print(f"An error occurred: {e}")