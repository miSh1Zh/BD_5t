from adapters.repositories.base import BaseRepository
import bcrypt
import pandas as pd
import numpy as np

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    hashed_password = hashed_password.decode("utf-8")
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class AuthorizationRepository(BaseRepository):
    def register_manager(self, login, password, name, paycheck):
        query = """
            INSERT INTO usr (login, hash_password, role)
            VALUES (%s, %s, %s) RETURNING id;
        """
        new_manager_id = self.fetchone("admin", query, (login, hash_password(password), "manager"))["id"]

        query = """
            INSERT INTO managers (id, name, paycheck)
            VALUES (%s, %s, %s);
        """
        self.execute("admin", query, (new_manager_id, name, paycheck))
        
        return new_manager_id

    def register_customer(self, login, password, name, phone):
        query = """
            INSERT INTO usr (login, hash_password)
            VALUES (%s, %s) RETURNING id;
        """
        new_customer_id = self.fetchone("admin", query, (login, hash_password(password)))["id"]

        query = """
            INSERT INTO customers (id, name, phone)
            VALUES (%s, %s, %s);
        """
        self.execute("admin", query, (new_customer_id, name, phone))
        
        return new_customer_id

    def login(self, login, password):
        query = """
            SELECT hash_password 
            FROM usr 
            WHERE login = %s;
        """
        hashed_password_res = self.fetchone("admin", query, (login,))
        account = [0, 0]
        if hashed_password_res:
            hashed_password = hashed_password_res["hash_password"]
            if check_password(password, hashed_password):
                query = """
                    SELECT id, role
                    FROM usr 
                    WHERE login = %s;
                """
                res = self.fetchone("admin", query, (login,))
                account[0] = res["id"]
                if res["role"] == "manager":
                    account[1] = 1
                elif res["role"] == "admin":
                    account[1] = 2
            else:
                account[0] = -1
        return account
