import os

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 10))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 40))


CACHE_TTL=int(os.getenv("CACHE_TTL", 60))
CACHE_KEY="orders:top"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
