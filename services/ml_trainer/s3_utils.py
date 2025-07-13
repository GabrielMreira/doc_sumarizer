import boto3
import os

BUCKET_NAME=os.getenv("S3_BUCKET_NAME")

def s3_upload(content: bytes, file_name_destiny : str):
    try:
        s3_client = boto3.client('s3')
        print(BUCKET_NAME)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name_destiny,
            Body=content
        )

        return f"s3://{BUCKET_NAME}/{file_name_destiny}"
    except Exception as e:
        raise

def read_from_s3(origin_file_name: str, temporary_file_path: str):
    try:
        s3_client = boto3.client('s3')

        s3_client.download_file(
            Bucket=BUCKET_NAME,
            Key=origin_file_name,
            Filename=temporary_file_path
        )
    except Exception as e:
        raise