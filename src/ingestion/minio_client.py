import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    # Prioriza o localhost:9000 do seu .env para evitar erros de conexão no WSL
    host = os.getenv('MINIO_HOST', 'localhost:9000')
    endpoint = f"http://{host}" if not host.startswith("http") else host
    
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
        region_name="us-east-1"
    )

def upload_file(file_path, bucket, object_name):
    """
    Envia arquivos locais para o MinIO. 
    Usado pelos scripts de scraping do Censo e CETIC.
    """
    s3 = get_s3_client()
    try:
        print(f"☁️ Fazendo upload de {os.path.basename(file_path)} para {bucket}/{object_name}")
        s3.upload_file(file_path, bucket, object_name)
    except Exception as e:
        print(f"❌ Erro no upload para o MinIO: {e}")
        raise e

def create_buckets():
    """
    Garante que a estrutura Raw, Trusted e Refined exista.
    """
    s3 = get_s3_client()
    buckets = ["raw", "trusted", "refined"]
    print("🛠️ Verificando estrutura de buckets...")
    for bucket in buckets:
        try:
            s3.head_bucket(Bucket=bucket)
            print(f"✅ Bucket '{bucket}' já existe.")
        except:
            print(f"🔨 Criando bucket: {bucket}")
            s3.create_bucket(Bucket=bucket)