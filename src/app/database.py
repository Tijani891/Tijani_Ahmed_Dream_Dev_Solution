import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Look for .env in the project root (two levels up from this file)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    dbname=os.getenv("DB_NAME", "moniepoint"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)