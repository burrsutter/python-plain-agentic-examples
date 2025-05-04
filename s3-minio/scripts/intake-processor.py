import os
import asyncio
import logging
import json
import tempfile # Added for temporary file handling
import aioboto3
from botocore.client import Config
from botocore.exceptions import ClientError
# Import necessary components from docling library
from docling.document_converter import DocumentConverter, ConversionStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('intake-processor')

# ----- Configuration from Environment -----
ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
REGION       = os.getenv("S3_DEFAULT_REGION", "us-east-1")
ACCESS_KEY   = os.getenv("S3_ACCESS_KEY_ID")
SECRET_KEY   = os.getenv("S3_SECRET_ACCESS_KEY")

# S3 bucket configuration
# All operations use the same bucket with different prefixes
SOURCE_BUCKET = "invoices"    # Main bucket name
SOURCE_PREFIX = "intake/"     # Prefix for files to be processed
DONE_PREFIX   = "done/"       # Prefix for successfully processed files
ERROR_PREFIX  = "error/"      # Prefix for files that failed processing
JSON_PREFIX   = "json/"       # Prefix for storing JSON output
POLL_INTERVAL = 5             # Seconds between polls

# ----- PDF to JSON Conversion -----
class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass

def convert_pdf_to_json(pdf_data: bytes, original_filename: str) -> dict:
    """
    Converts PDF binary data to JSON using DocumentConverter.

    Args:
        pdf_data (bytes): The binary content of the PDF file.
        original_filename (str): The original filename for logging.

    Returns:
        dict: The JSON representation of the PDF document.

    Raises:
        ConversionError: If conversion fails.
    """
    logger.info(f"Starting conversion for '{original_filename}'")
    temp_path = None
    try:
        # Create a temporary file to store the PDF data
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_data)
            temp_path = temp_file.name
            logger.debug(f"PDF data written to temporary file: {temp_path}")

        # Initialize the converter
        converter = DocumentConverter()

        # Convert the PDF document from the temporary file path
        logger.info(f"Calling converter.convert for temp file: {temp_path}")
        conversion_result = converter.convert(temp_path, raises_on_error=True)

        # Check conversion status
        if conversion_result.status not in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS):
            error_msg = f"Docling conversion failed for {original_filename} with status: {conversion_result.status}"
            if conversion_result.errors:
                 error_messages = [f"{e.component_type}: {e.error_message}" for e in conversion_result.errors]
                 error_msg += f" Errors: {'; '.join(error_messages)}"
            logger.error(error_msg)
            raise ConversionError(error_msg)

        logger.info(f"Docling conversion successful for {original_filename}.")
        docling_doc = conversion_result.document

        # Export the document to JSON dictionary
        # Assuming export_to_dict() is the correct method based on previous context
        if hasattr(docling_doc, 'export_to_dict'):
            json_data = docling_doc.export_to_dict()
            logger.info(f"Successfully exported DoclingDocument to dict for {original_filename}.")
            # Add metadata if needed (optional)
            json_data['metadata'] = {
                'original_filename': original_filename,
                'file_size_bytes': len(pdf_data),
                'conversion_status': str(conversion_result.status)
            }
            return json_data
        else:
            methods = [m for m in dir(docling_doc) if not m.startswith('_') and callable(getattr(docling_doc, m))]
            logger.error(f"Could not find 'export_to_dict' method on DoclingDocument. Available methods: {methods}")
            raise ConversionError("Could not find 'export_to_dict' method on DoclingDocument.")

    except Exception as e:
        # Catch any exception during the process
        error_msg = f"Error during PDF to JSON conversion for {original_filename}: {str(e)}"
        logger.exception(error_msg) # Log exception with traceback
        raise ConversionError(error_msg) from e
    finally:
        # Clean up the temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug(f"Deleted temporary file {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")


# --- Main Processing Function ---
async def process_file(key: str, data: bytes):
    """
    Process a file from the S3 bucket.
    
    Args:
        key (str): The S3 object key
        data (bytes): The file content as bytes
        
    Returns:
        None
        
    For PDF files, this function converts them to JSON using the
    DocumentConverter from the docling library.
    """
    logger.info(f"Processing {key}: {len(data)} bytes")
    
    # Get the filename from the key
    filename = os.path.basename(key)
    
    # Check if this is a PDF file
    if filename.lower().endswith('.pdf'):
        try:
            # Convert PDF to JSON
            logger.info(f"Converting PDF file: {filename}")
            json_data = convert_pdf_to_json(data, filename)
            
            # Log some information about the conversion
            logger.info(f"Successfully converted {filename} to JSON")
            
            # Return the JSON data for further processing or storage
            return json_data
            
        except ConversionError as e:
            logger.error(f"Conversion error for {filename}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {filename}: {str(e)}")
            raise
    else:
        logger.warning(f"File {filename} is not a PDF, skipping conversion")
        # For non-PDF files, we could implement other processing logic
        # or simply pass them through

async def watch_and_transfer():
    """
    Main function that watches the S3 bucket for new files,
    processes them, and moves them to the appropriate destination.
    
    This function runs in an infinite loop, polling the bucket
    at regular intervals defined by POLL_INTERVAL.
    """
    logger.info(f"Starting intake processor watching {SOURCE_BUCKET}/{SOURCE_PREFIX}")
    logger.info(f"Successfully processed files will be moved to {SOURCE_BUCKET}/{DONE_PREFIX}")
    logger.info(f"JSON files will placed at {SOURCE_BUCKET}/{JSON_PREFIX}")
    logger.info(f"Failed files will be moved to {SOURCE_BUCKET}/{ERROR_PREFIX}")

    
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
        config=Config(signature_version="s3v4"),
        verify=False  # set True if you have valid SSL certs
    ) as s3:
        while True:
            try:
                # List objects in the intake prefix
                resp = await s3.list_objects_v2(
                    Bucket=SOURCE_BUCKET,
                    Prefix=SOURCE_PREFIX
                )
                
                # Process each file found
                for obj in resp.get("Contents", []):
                    key = obj["Key"]
                    if key.endswith("/"):
                        continue  # skip folder markers
                    
                    logger.info(f"Found file to process: {key}")
                    
                    try:
                        # Download and process the file
                        download = await s3.get_object(Bucket=SOURCE_BUCKET, Key=key)
                        body = await download["Body"].read()
                        
                        # Extract the filename from the key (remove the prefix)
                        filename = os.path.basename(key)
                        
                        # Process the file and get the JSON result
                        json_result = await process_file(key, body)
                        
                        # If it's a PDF file and we have JSON data, store it
                        if filename.lower().endswith('.pdf') and json_result:
                            # Create a JSON file with the same base name
                            json_key = f"{JSON_PREFIX}{os.path.splitext(filename)[0]}.json"
                            logger.info(f"Storing JSON result to {json_key}")
                            
                            # Convert JSON to string
                            json_content = json.dumps(json_result, indent=2)
                            
                            # Upload the JSON file
                            await s3.put_object(
                                Bucket=SOURCE_BUCKET,
                                Key=json_key,
                                Body=json_content
                            )
                        
                        # On success, move to done prefix with .done suffix
                        done_key = f"{DONE_PREFIX}{filename}.done"
                        logger.info(f"Processing successful, moving to {done_key}")
                        
                        await s3.copy_object(
                            Bucket=SOURCE_BUCKET,
                            CopySource={"Bucket": SOURCE_BUCKET, "Key": key},
                            Key=done_key
                        )
                    except Exception as e:
                        # On error, move to error prefix with .error suffix
                        filename = os.path.basename(key)
                        error_key = f"{ERROR_PREFIX}{filename}.error"
                        logger.error(f"Error processing {key}: {str(e)}")
                        
                        await s3.copy_object(
                            Bucket=SOURCE_BUCKET,
                            CopySource={"Bucket": SOURCE_BUCKET, "Key": key},
                            Key=error_key
                        )
                    finally:
                        # Delete the original in all cases
                        await s3.delete_object(Bucket=SOURCE_BUCKET, Key=key)
                        logger.info(f"Removed {key} from source")
                
                # Wait before next poll
                await asyncio.sleep(POLL_INTERVAL)
                
            except Exception as e:
                # Catch any unexpected errors in the main loop
                logger.error(f"Unexpected error in main loop: {str(e)}")
                # Wait before retry
                await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        logger.info("Starting intake processor")
        asyncio.run(watch_and_transfer())
    except KeyboardInterrupt:
        logger.info("Intake processor stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")