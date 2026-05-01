from src.ingestion.minio_client import get_s3_client

s3 = get_s3_client()

response = s3.list_buckets()

for bucket in response.get("Buckets", []):
    print("🪣", bucket["Name"])