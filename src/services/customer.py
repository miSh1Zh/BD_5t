from adapters.repositories.customer import CustomerRepository
import pandas as pd
import numpy as np


class CustomerService: 
    def __init__(self):
        self._repo: CustomerRepository = CustomerRepository()

    def get_restaurants(self):
        res = pd.DataFrame(self._repo.get_restaurants())
        return res
    def get_menu(self, adress: str):
        res = pd.DataFrame(self._repo.get_menu(adress))
        return res
    def get_events(self, adress: str):
        res = pd.DataFrame(self._repo.get_events(adress))
        return res
    def make_order(self, adress: str, bill: int, customer_id: int, dish_list: pd.DataFrame):
        dish_list_json = dish_list.to_json(orient='records')
        self._repo.make_order(adress, bill, customer_id, dish_list_json)
    def get_self_info(self, customer_id: int):
        return self._repo.get_self_info(customer_id)
    def view_orders(self, customer_id: int, grouping: str):
        if grouping == "all":
            res = pd.DataFrame(self._repo.view_orders(customer_id))
            return res
        else:
            res = pd.DataFrame(self._repo.view_orders_with_dish(customer_id, grouping))
            return res
