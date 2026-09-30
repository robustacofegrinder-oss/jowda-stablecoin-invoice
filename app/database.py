import os
import psycopg2

def get_connection():
    host = os.environ["DB_HOST"]
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "postgres")
    user = os.environ["DB_USER"]
    print(f"DB_DEBUG: host={host} port={port} dbname={dbname} user={user}", flush=True)
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=os.environ["DATABASE_PASSWORD"],
    )

def init_db():
    return True
