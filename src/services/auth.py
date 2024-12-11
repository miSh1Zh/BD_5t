from adapters.repositories.auth import AuthorizationRepository
import pandas as pd
import numpy as np

class AuthorizationService:
    def __init__(self):
        self._repo: AuthorizationRepository = AuthorizationRepository()

    def register_manager(self, login: str, password: str, name: str, paycheck: int):
        return self._repo.register_manager(login, password, name, paycheck)
    def register_customer(self, login: str, password: str, name: str, phone: str): 
        return self._repo.register_customer(login, password, name, phone)
    def login(self, login: str, password: str):
        return self._repo.login(login, password)
