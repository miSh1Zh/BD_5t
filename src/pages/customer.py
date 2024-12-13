import streamlit as st
from services.customer import CustomerService
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

service = CustomerService()
 
def show_make_order_page():
    st.title("Make order")
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants()
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant:", adresses)

    if "order_list_products" not in st.session_state:
        st.session_state.order_list_products = pd.DataFrame(
            columns=["name", "price", "quanity", "dish_id"]
        )
    st.session_state.menu = service.get_menu(selected_adress)

    if st.session_state.menu.shape[0] > 0:

        categories = [categ for categ in set(st.session_state.menu["category"].to_list())]
        category = st.selectbox("Select dish category:", categories)


        dishes = [dish for dish in st.session_state.menu["name"][st.session_state.menu["category"] == category]]
        selected_dish = st.selectbox("Select dish:", dishes)

        quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)

        if st.button("Add dish"):
            dish_info = st.session_state.menu[st.session_state.menu["name"] == selected_dish]
            dish_info["quanity"] = [quantity] 
            st.session_state.order_list_products = pd.concat(
                [st.session_state.order_list_products, dish_info], ignore_index=True
            )

        st.write(f"Bill: {(st.session_state.order_list_products.price * st.session_state.order_list_products.quanity).sum()}")
        st.dataframe(st.session_state.order_list_products[["name", "price", "quanity"]], hide_index=True)
        
        if st.button("Clear order"):
            st.session_state.order_list_products = pd.DataFrame(
                columns=["name", "price", "quanity", "dish_id"]
            )
        
        if st.button("Make order") and len(st.session_state.order_list_products["name"]) > 0:
            list_products = st.session_state.order_list_products.groupby(["name", "dish_id"]).agg({"price": 'mean', "quanity": 'sum'}).reset_index()
            list_products["price"] = list_products["price"] * list_products["quanity"]
            # st.dataframe(list_products)
            service.make_order(selected_adress, sum(list_products["price"]), st.session_state.id, list_products[["dish_id", "quanity"]]) 
            st.write(f"Your order has been sent for approval")
            st.session_state.order_list_products = pd.DataFrame(
                columns=["name", "price", "quanity", "dish_id"]
            )
    else:
        st.write("No menu in selected restaurant")




def show_customer_orders_page():
    st.title("Orders")
    selected_dish = "all"
    if "orders_table" not in st.session_state:
        st.session_state.grouping = "all"
        st.session_state.orders_table = service.view_orders(st.session_state.id, st.session_state.grouping)
        st.session_state.grouping_updated_at = datetime.now()

    elif st.session_state.grouping != selected_dish or st.session_state.grouping_updated_at < (datetime.now() - timedelta(seconds=30)):
        st.session_state.grouping = selected_dish
        st.session_state.orders_table = service.view_orders(st.session_state.id, st.session_state.grouping)
        st.session_state.grouping_updated_at = datetime.now()
    
    try:
        st.dataframe(st.session_state.orders_table.rename(columns={"adress": "Adress", "bill": "Bill", "dish_list": "Dishes"})[["Adress", "Bill", "Dishes"]], hide_index=True)
    except:
        st.write("You have no approved orders yet")



def show_events_page():
    st.title("Events")
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants()
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant:", adresses)
    st.session_state.events_table = service.get_events(selected_adress).rename(columns={"name": "Event", "date": "Date", "start_hour": "Start" , "end_hour": "End"})
    st.dataframe(st.session_state.events_table, hide_index=True)
    


def main_customer():
    info = service.get_self_info(st.session_state.id)
    st.write("Welcome, ", info[0])
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select:",
        ["Make order", "View orders", "Events"]
    )
    if page == "Make order":
        show_make_order_page()
    elif page == "View orders":
        show_customer_orders_page()
    elif page == "Events":
        show_events_page()
