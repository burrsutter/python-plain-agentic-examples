import os
import json
import tempfile
import logging
from docling.document_converter import DocumentConverter

# Configure logging
logger = logging.getLogger('docling-converter')

class ConversionError(Exception):
    """Exception raised for errors during document conversion."""
    pass

def convert_pdf_to_json(pdf_data: bytes, filename: str) -> dict:
    """
    Convert PDF binary data to JSON using DocumentConverter.
    
    Args:
        pdf_data (bytes): The binary content of the PDF file
        filename (str): The original filename, used for logging and metadata
        
    Returns:
        dict: The JSON representation of the PDF document
        
    Raises:
        ConversionError: If conversion fails for any reason
    """
    if not filename.lower().endswith('.pdf'):
        raise ConversionError(f"File {filename} is not a PDF file")
    
    logger.info(f"Converting {filename} to JSON")
    
    # Create a temporary file to store the PDF data
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        try:
            # Write PDF data to the temporary file
            temp_file.write(pdf_data)
            temp_file.flush()
            temp_path = temp_file.name
            
            # Close the file so DocumentConverter can access it
            temp_file.close()
            
            # Initialize the DocumentConverter
            converter = DocumentConverter()
            
            # Convert the PDF to JSON
            result = converter.convert_to_json(temp_path)
            
            # Add metadata about the original file
            result['metadata'] = {
                'original_filename': filename,
                'file_size_bytes': len(pdf_data),
                'conversion_timestamp': converter.get_timestamp()
            }
            
            logger.info(f"Successfully converted {filename} to JSON")
            return result
            
        except Exception as e:
            error_msg = f"Error converting {filename} to JSON: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e
        
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")

def save_json_to_file(json_data: dict, output_path: str) -> None:
    """
    Save JSON data to a file.
    
    Args:
        json_data (dict): The JSON data to save
        output_path (str): The path where to save the JSON file
        
    Raises:
        IOError: If saving fails
    """
    try:
        with open(output_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=2)
        logger.info(f"JSON data saved to {output_path}")
    except Exception as e:
        error_msg = f"Error saving JSON to {output_path}: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg) from e