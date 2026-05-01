# import os
# import duckdb
# from dotenv import load_dotenv

# # Carrega as variáveis de ambiente do arquivo .env
# load_dotenv()

# def get_duckdb_connection():
#     """
#     Cria uma conexão DuckDB configurada para acessar o MinIO local via S3.
#     """
#     # Inicia uma conexão em memória
#     con = duckdb.connect()
    
#     # Instala e carrega a extensão necessária para protocolos HTTP/S3
#     con.execute("INSTALL httpfs;")
#     con.execute("LOAD httpfs;")
    
#     # Configurações do MinIO
#     # O endpoint geralmente é localhost:9000 no seu ambiente Docker/WSL
#     endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
#     access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
#     secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    
#     con.execute(f"""
#         SET s3_endpoint='{endpoint}';
#         SET s3_access_key_id='{access_key}';
#         SET s3_secret_access_key='{secret_key}';
#         SET s3_use_ssl=false;
#         SET s3_url_style='path';
#     """)
    
#     return con

# def query_to_df(query):
#     """
#     Função utilitária para rodar uma query e retornar um DataFrame do Pandas.
#     """
#     con = get_duckdb_connection()
#     return con.execute(query).df()

# import os
# import duckdb
# from dotenv import load_dotenv

# load_dotenv()

# def get_duckdb_connection():
#     con = duckdb.connect()

#     con.execute("INSTALL httpfs;")
#     con.execute("LOAD httpfs;")

#     endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")

#     con.execute(f"SET s3_endpoint='{endpoint}';")
#     con.execute(f"SET s3_access_key_id='{os.getenv('MINIO_ACCESS_KEY', 'minioadmin')}';")
#     con.execute(f"SET s3_secret_access_key='{os.getenv('MINIO_SECRET_KEY', 'minioadmin')}';")

#     con.execute("SET s3_use_ssl=false;")
#     con.execute("SET s3_url_style='path';")

#     return con
import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

def get_duckdb_connection():
    con = duckdb.connect()

    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")

    # 🔥 garante valor válido
    endpoint = os.getenv("MINIO_HOST", "localhost:9000")
    endpoint = endpoint.replace("http://", "").replace("https://", "")

    con.execute(f"""
    SET s3_endpoint='{endpoint}';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
    """)

    con.execute(f"SET s3_access_key_id='{os.getenv('MINIO_ACCESS_KEY', 'minioadmin')}';")
    con.execute(f"SET s3_secret_access_key='{os.getenv('MINIO_SECRET_KEY', 'minioadmin')}';")

    return con