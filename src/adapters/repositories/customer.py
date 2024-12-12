from adapters.repositories.base import BaseRepository

class CustomerRepository(BaseRepository):
    def get_restaurants(self):
        query = """
            SELECT adress, open_hour, close_hour, phone, email
            FROM restaurants
            ORDER BY id;
        """
        return self.fetchall("customer", query)
    
    def get_menu(self, adress):
        query = """
            SELECT category, name, price, dish_id
            FROM menu_in_restaurants
            WHERE adress = %s
            ORDER BY category;
        """
        return self.fetchall("customer", query, (adress,))
    
    def get_events(self, adress):
        query = """
            SELECT name, date, start_hour, end_hour
            FROM events_in_restaurants
            WHERE adress = %s and date > current_date;
        """
        return self.fetchall("customer", query, (adress,))
    
    def make_order(self, adress, bill, customer_id, dish_list):
        # query = """
        #     SELECT id
        #     FROM restaurants
        #     WHERE adress = %s;
        # """
        # restaurant_id = self.fetchone("customer", query, (adress,))["id"]

        # query = """
        #     INSERT INTO 
        #         orders (bill, customer_id, restaurant_id)
        #     VALUES
        #         (%s, %s, %s) 
        #     RETURNING id; 
        # """
        # order_id = self.fetchone("admin", query, (bill, customer_id, restaurant_id))["id"]
        
        # query = """
        #     INSERT INTO 
        #         orders_dishes (order_id, dish_id, positions_in_order)
        #     VALUES
        #         (%s, %s, %s) 
        # """
        # for dish in dish_list["dish_id"]:
        #     quanity = dish_list["quanity"][dish_list["dish_id"] == dish].to_list()[0]
        #     self.execute("customer", query, (order_id, dish, quanity))

        query = """
            CALL make_order(%s::VARCHAR(255), %s::INT, %s::INT, %s::JSONB);
        """

        self.execute("admin", query, (adress, bill, customer_id, dish_list))
    
    def get_self_info(self, customer_id):
        query = """
            SELECT name, phone
            FROM customers
            WHERE id = %s;
        """
        res = self.fetchone("customer", query, (customer_id,))
        return [res["name"], res["phone"]]
    
    
    def view_orders(self, customer_id):
        query = """
            SELECT name, adress, order_id, dish_list, bill
            FROM bills
            WHERE customer_id = %s;
        """
        return self.fetchall("customer", query, (customer_id,))
    
    def view_orders_with_dish(self, customer_id, dish_name):
        query = """
            CALL search_dish_in_orders(%s, %s);
        """
        return self.fetchall("customer", query, (dish_name, customer_id))

    # def delete_order(self, order_id):
    #     query = """
    # 
    #     """
    #     return self.execute("customer", query, (order_id,))
    