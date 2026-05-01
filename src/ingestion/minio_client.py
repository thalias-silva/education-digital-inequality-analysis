import boto3
import os


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{os.getenv('MINIO_HOST', 'localhost:9000')}",
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin")
    )


def upload_file(file_path, bucket, object_name):
    s3 = get_s3_client()
    print(f"☁️ Upload: {object_name}")
    s3.upload_file(file_path, bucket, object_name)