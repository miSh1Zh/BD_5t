from adapters.repositories.base import BaseRepository
import pandas as pd
import numpy as np


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
        query = """
            SELECT adress, restaurant_id, phone, email, open_hour, close_hour
            FROM 
                managers_restaurants mr
                INNER JOIN restaurants r on r.id = mr.restaurant_id 
            WHERE manager_id = %s;
        """
        return self.fetchall("manager", query, (manager_id,))
    
    def get_unapproved_orders(self, restaurant_id):
        query = """
            SELECT o.id AS order_id, name, phone, bill
            FROM 
                orders o
                INNER JOIN customers c on c.id = o.customer_id

            WHERE restaurant_id = %s and approved = false
            ORDER BY order_id ASC;
        """
        return self.fetchall("manager", query, (restaurant_id,))
    
    def approve_order(self, order_id):
        query = """
            UPDATE orders
            SET approved = true
            WHERE id = %s;
        """
        self.execute("manager", query, (order_id,))
        