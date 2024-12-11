import os
from dotenv import load_dotenv

load_dotenv("env.env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 10))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 40))
    