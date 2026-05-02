import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

def get_duckdb_connection():
    con = duckdb.connect()
    
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    
    endpoint = os.getenv("MINIO_HOST", "127.0.0.1:9000").replace("http://", "")
    
    con.execute(f"SET s3_endpoint='{endpoint}';")
    con.execute(f"SET s3_access_key_id='{os.getenv('MINIO_ACCESS_KEY')}';")
    con.execute(f"SET s3_secret_access_key='{os.getenv('MINIO_SECRET_KEY')}';")
    con.execute("SET s3_use_ssl=false;")
    con.execute("SET s3_url_style='path';")
    
    return con