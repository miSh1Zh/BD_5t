import psycopg2.pool
from contextlib import contextmanager
import logging
import atexit
import sys
from settings import POOL_MIN_CONN, POOL_MAX_CONN, DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASSWORD


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
