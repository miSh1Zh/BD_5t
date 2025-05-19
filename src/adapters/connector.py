import psycopg2.pool
from contextlib import contextmanager
import logging
import atexit
import redis
from datetime import timedelta
import sys
import json
from settings import POOL_MIN_CONN, POOL_MAX_CONN, DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASSWORD, REDIS_DB, REDIS_HOST, REDIS_PORT, CACHE_TTL


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

def put_cache_data(key, data, ttl=CACHE_TTL):
    logger.info(f"Put data to redis with key = {key}...")
    redis_client.set(key, json.dumps(data), ex=ttl)
    logger.info("Done")

def get_cache_data(key):
    logger.info(f"Try to get data with key = {key}...")
    cached = redis_client.get(key)

    if cached:
        logger.info(f"Get data with key = {key}")
        return json.loads(cached)
    logger.info(f"No data with key = {key} was found")
    return None

def delete_cache_data(key):
    logger.info(f'Try to delete cache for key = {key}...')
    try:
        logger.info(f'Delete {key}')
        redis_client.delete(key)
    except:
        logger.error(f'No cache {key}')
        raise

def create_pubsub():
    """Создает объект pubsub для подписки на каналы"""
    try:
        return redis_client.pubsub()
    except Exception as e:
        logger.error(f"Failed to create pubsub: {str(e)}")
        raise

def subscribe_to_channel(pubsub, channel):
    """Подписывается на указанный канал"""
    try:
        logger.info(f"Subscribing to channel: {channel}")
        pubsub.subscribe(channel)
        # Получаем первое сообщение подписки (подтверждение подписки)
        pubsub.get_message(timeout=1.0)
        return pubsub
    except Exception as e:
        logger.error(f"Failed to subscribe to channel {channel}: {str(e)}")
        raise

def publish_message(channel, message):
    """Публикует сообщение в указанный канал"""
    try:
        logger.info(f"Publishing message to channel {channel}")
        return redis_client.publish(channel, json.dumps(message))
    except Exception as e:
        logger.error(f"Failed to publish message to channel {channel}: {str(e)}")
        raise

def listen_for_messages(pubsub, callback, timeout=None):
    """
    Слушает сообщения из подписки и вызывает callback для каждого сообщения.
    callback должен принимать один аргумент - сообщение.
    """
    try:
        while True:
            message = pubsub.get_message(timeout=timeout)
            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    callback(data)
                except json.JSONDecodeError:
                    callback(message['data'])
    except Exception as e:
        logger.error(f"Error in listen_for_messages: {str(e)}")
        raise

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
