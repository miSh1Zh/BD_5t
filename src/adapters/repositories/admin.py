from adapters.repositories.base import BaseRepository

class AdminRepository(BaseRepository):
    def get_managers(self):
        query = """
            SELECT m.id AS id, name, paycheck, ARRAY_AGG(phone) as phone, ARRAY_AGG(adress) AS adresses
            FROM 
                managers m
                INNER JOIN managers_restaurants mr on mr.manager_id = m.id
                INNER JOIN restaurants r on r.id = mr.restaurant_id
            GROUP BY m.id, name, paycheck;
        """
        return self.fetchall("admin", query)
    
    def get_restaurants(self):
        query = """
            SELECT id AS restaurant_id, adress, open_hour, close_hour, phone, email
            FROM restaurants;
        """
        return self.fetchall("admin", query)
    
    def add_restaurant(self, adress, phone, email):
        query = """
            INSERT INTO 
                restaurants (adress, phone, email)
            VALUES
                (%s, %s, %s) RETURNING id; 
        """
        return self.fetchone("admin", query, (adress, phone, email))["id"]
    
    def place_manager(self, manager_id, restaurant_id):
        query = """
            INSERT INTO 
                managers_restaurants (manager_id, restaurant_id)
            VALUES
                (%s, %s); 
        """
        self.execute("admin", query, (manager_id, restaurant_id))
    
    def get_statistic(self):
        query = """
            SELECT adress, avg_approve_time, total_month_income
            FROM chain_statistic;
        """
        return self.fetchall("admin", query)
        