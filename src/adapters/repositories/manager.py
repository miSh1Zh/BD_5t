from adapters.repositories.base import BaseRepository
import threading
import json

from adapters.connector import get_cache_data, put_cache_data, create_pubsub, subscribe_to_channel, listen_for_messages, publish_message, delete_cache_data

CACHE_KEY = "manager"


def start_cache_invalidator(channel):
        """Фоновый поток для обработки сообщений об инвалидации кеша"""
        def listener():
            pubsub = create_pubsub()
            subscribe_to_channel(pubsub, channel)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        if data:
                            cache_key = data
                            delete_cache_data(cache_key)
                    except:
                        continue

        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
    
start_cache_invalidator(f'{CACHE_KEY}:unapproved_orders')

class ManagerRepository(BaseRepository):
    def add_dish(self, name, category, price):
        query = """
            INSERT INTO 
                dishes (name, category, price)
            VALUES
                (%s, %s, %s) RETURNING id; 
        """
        return self.fetchone("admin", query, (name, category, price))["id"]
    
    def place_dish(self, dish_id, restaurant_id):
        query = """
            INSERT INTO 
                dishes_restaurants (dish_id, restaurant_id)
            VALUES
                (%s, %s); 
        """
        self.execute("manager", query, (dish_id, restaurant_id))
    
    def add_event(self, name, description, restaurant_id, start_datetime, duration):
        query = """
            INSERT INTO 
                events (name, description, start_datetime, duration, restaurant_id)
            VALUES
                (%s, %s, %s, %s, %s) RETURNING id; 
        """
        return self.fetchone("admin", query, (name, description, start_datetime, duration, restaurant_id))["id"]

    def get_self_info(self, manager_id):
        query = """
            SELECT name, paycheck
            FROM managers
            WHERE id = %s;
        """
        res = self.fetchone("manager", query, (manager_id,))
        return [res["name"], str(res["paycheck"])]
    
    def get_restaurants(self, manager_id):
        cur_key = f'{CACHE_KEY}:restaurants' 
        data = None
        if not data:
            query = """
                SELECT adress, restaurant_id, phone, email, open_hour, close_hour
                FROM 
                    managers_restaurants mr
                    INNER JOIN restaurants r on r.id = mr.restaurant_id 
                WHERE manager_id = %s;
            """
            data = self.fetchall("manager", query, (manager_id,))
        return data
    
    def get_unapproved_orders(self, restaurant_id):
        cur_key = f"{CACHE_KEY}:unapproved_orders"
        data = get_cache_data(cur_key)
        if not data:
            query = """
                SELECT o.id AS order_id, name, phone, bill
                FROM 
                    orders o
                    INNER JOIN customers c on c.id = o.customer_id

                WHERE restaurant_id = %s and approved = false
                ORDER BY order_id ASC;
            """
            data = self.fetchall("manager", query, (restaurant_id,))
            put_cache_data(cur_key, data)
        return data
    
    def approve_order(self, order_id, restaurant_id):
        query = """
            UPDATE orders
            SET approved = true
            WHERE id = %s;
        """
        self.execute("manager", query, (order_id,))
        cur_key = f"{CACHE_KEY}:unapproved_orders"
        message = cur_key
        publish_message(cur_key, message)
        