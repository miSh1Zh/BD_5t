from adapters.repositories.manager import ManagerRepository
import pandas as pd
import numpy as np
from datetime import datetime

class ManagerService:
    def __init__(self):
        self._repo: ManagerRepository = ManagerRepository()
    
    def add_dish(self, name: str, category: str, price: int):
        return self._repo.add_dish(name, category, price)
    def place_dish(self, dish_id: int, restaurant_id: int):
        return self._repo.place_dish(dish_id, restaurant_id)
    def add_event(self, name: str, description: str, restaurant_id: int, start_datetime: datetime, duration: int):
        return self._repo.add_event(name, description, restaurant_id, start_datetime, duration)
    def get_self_info(self, manager_id: int):  
        return self._repo.get_self_info(manager_id)   
    def get_restaurants(self, manager_id: int):
        return pd.DataFrame(self._repo.get_restaurants(manager_id))
    def get_unapproved_orders(self, restaurant_id: int):
        return pd.DataFrame(self._repo.get_unapproved_orders(restaurant_id))
    def approve_order(self, order_id: int, restaurant_id: int):
        self._repo.approve_order(order_id, restaurant_id)
