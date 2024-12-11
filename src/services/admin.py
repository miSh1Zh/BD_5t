from adapters.repositories.admin import AdminRepository
import pandas as pd 
import numpy as np


class AdminService:
    def __init__(self):
        self._repo: AdminRepository = AdminRepository()

    def get_managers(self):
        return pd.DataFrame(self._repo.get_managers())
    def get_restaurants(self):
        return pd.DataFrame(self._repo.get_restaurants())
    def add_restaurant(self, adress: str, phone: str, email: str):
        return self._repo.add_restaurant(adress, phone, email)
    def place_manager(self, manager_id: int, restaurant_id: int):
        self._repo.place_manager(manager_id, restaurant_id)
    def get_statistic(self):
        return pd.DataFrame(self._repo.get_statistic())