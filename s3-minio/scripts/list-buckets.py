import os
import boto3
from botocore.client import Config

# Read MinIO endpoint and credentials from environment
endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
access_key = os.getenv("S3_ACCESS_KEY_ID")
secret_key = os.getenv("S3_SECRET_ACCESS_KEY")

# Create an S3 client pointing at MinIO
s3_client = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(signature_version='s3v4'),
    verify=False  # set to True if you have valid SSL certificates
)

# Example usage: list buckets
response = s3_client.list_buckets()
for bucket in response.get("Buckets", []):
    print(bucket["Name"])