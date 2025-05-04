import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Read configuration from environment
endpoint_url = os.getenv("S3_ENDPOINT_URL")  # e.g., http://localhost:9000
region      = os.getenv("S3_DEFAULT_REGION", "us-east-1")
access_key  = os.getenv("S3_ACCESS_KEY_ID")
secret_key  = os.getenv("S3_SECRET_ACCESS_KEY")

# Create an S3 client (works for AWS S3 or any S3-compatible service)
s3_client = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region,
    config=Config(signature_version='s3v4'),
    verify=False  # Change to True if using valid SSL certificates
)

# Attempt to create the bucket
bucket_name = 'mypythonbucket'
try:
    if region == 'us-east-1':
        # us-east-1 does not require LocationConstraint
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    print(f"Bucket '{bucket_name}' created successfully.")
except ClientError as e:
    print(f"Error creating bucket: {e}")