import psycopg2.pool
from contextlib import contextmanager
import logging
import atexit
import redis
from datetime import timedelta
import sys
from settings import POOL_MIN_CONN, POOL_MAX_CONN, DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASSWORD, REDIS_DB, REDIS_HOST, REDIS_PORT 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("Initializing connection pool...")
try:
    connection_pool_allmight = psycopg2.pool.SimpleConnectionPool(POOL_MIN_CONN, POOL_MAX_CONN, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT)
    connection_pool_managers = psycopg2.pool.SimpleConnectionPool(POOL_MIN_CONN, POOL_MAX_CONN, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT, options='-c role=manager')
    connection_pool_customers = psycopg2.pool.SimpleConnectionPool(POOL_MIN_CONN, POOL_MAX_CONN, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT, options='-c role=customer')
except:
    logger.info(f"Could not connect to database with params: name={DB_NAME}, host={DB_HOST}, user={DB_USER}, port={DB_PORT}")
    sys.exit(1)

@contextmanager
def get_connection(role):
    if role == "admin":
        connection = connection_pool_allmight.getconn()
    elif role == "manager":
        connection = connection_pool_managers.getconn()
    elif role == "customer":
        connection = connection_pool_customers.getconn()
    try:
        yield connection
    finally:
        if role == "admin":
            connection_pool_allmight.putconn(connection)
        elif role == "manager":
            connection_pool_managers.putconn(connection)
        elif role == "customer":
            connection_pool_customers.putconn(connection)


####################################################

logger.info(f"Initializing redis with host={REDIS_HOST}, db={REDIS_DB} on port {REDIS_PORT}")
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
except:
    logger.info(f"Could not connect to redis with params: host={REDIS_HOST}, db={REDIS_DB}, port {REDIS_PORT}")
    sys.exit(1)

def get_redis_client():
    try:
        return redis_client
    except:
        logger.info(f"No redis_client returned")
        sys.exit(2)

def get_cached_data(key, fetch_func, ttl=300):
    cached = redis_client.get(key)
    if cached:
        return pickle.loads(cached)
    data = fetch_func()
    redis_client.setex(key, ttl, pickle.dumps(data))
    return data


####################################################

def close_connection_pool():
    if connection_pool_managers:
        connection_pool_managers.closeall()
        logger.info("Connection pool for managers closed.")
    if connection_pool_customers:
        connection_pool_customers.closeall()
        logger.info("Connection pool for customers closed.")
    if connection_pool_allmight:
        connection_pool_allmight.closeall()
        logger.info("Connection pool for admin closed.")


def on_exit():
    logger.info("Close application...")
    close_connection_pool()


atexit.register(on_exit)
