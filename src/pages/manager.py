import streamlit as st
from services.manager import ManagerService
from services.customer import CustomerService
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


service = ManagerService()

def show_menu_page(): # добавить блюдо и разместить его в ресторанах
    st.title("Add new position to menu")
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants(st.session_state.id)
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant:", adresses)
    selected_restaurant_info = st.session_state.restaurants[st.session_state.restaurants["adress"] == selected_adress]
    selected_restaurant_id = selected_restaurant_info["restaurant_id"].to_list()[0]

    if ("update_menu" not in st.session_state) or (st.session_state.update_menu) or ("menu" not in st.session_state and "last_menu_update" not in st.session_state) or (st.session_state.last_menu_update < (datetime.now() - timedelta(seconds=20))):
        st.session_state.menu = CustomerService().get_menu(selected_adress)
        st.session_state.last_menu_update = datetime.now()
        st.session_state.update_manu = False

    st.dataframe(st.session_state.menu.rename(columns={"name": "Dish", "category": "Category", "price": "Price"})[["Dish", "Category", "Price"]], hide_index=True)

    dish_name = st.text_input("New dish")
    categories = [categ for categ in set(st.session_state.menu["category"].to_list())]
    category = st.selectbox("Select dish category:", categories)
    price = st.number_input("Price", format="%0.1f", min_value=150.0, step=50.0)
    
    
    if st.button("Add dish"):
        try:
            new_dish_id = service.add_dish(dish_name, category, int(price))
            service.place_dish(new_dish_id, selected_restaurant_id)
            st.write(f"Add {dish_name} to menu in restaurant at {selected_adress}")
            st.session_state.update_manu = True
        except:   
            st.write("Dish with this name is already in the menu")


def show_orders_page():
    st.title("Orders")
    
    
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants(st.session_state.id)
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant:", adresses)    
    selected_restaurant_info = st.session_state.restaurants[st.session_state.restaurants["adress"] == selected_adress]
    selected_restaurant_id = selected_restaurant_info["restaurant_id"].to_list()[0]

    if "rest" not in st.session_state:
        st.session_state.rest = selected_restaurant_id
    
    
    if ("update_orders" not in st.session_state) or (st.session_state.update_orders) or (st.session_state.rest != selected_restaurant_id) or ("orders_table" not in st.session_state and "last_orders_update" not in st.session_state) or (st.session_state.last_orders_update < (datetime.now() - timedelta(seconds=20))):
        st.session_state.orders_table = service.get_unapproved_orders(selected_restaurant_id)
        st.session_state.rest = selected_restaurant_id
        st.session_state.last_orders_update = datetime.now()
        st.session_state.update_orders = False
    

    if st.session_state.orders_table.shape[0] != 0:
        st.dataframe(st.session_state.orders_table.rename(columns={"order_id": "Order", "name": "Customer", "bill": "Bill", "phone": "Phone"}), hide_index=True)
        order_to_approve = st.number_input("Order to approve", min_value=1, format="%d", step=1)
        if st.button("Approve"):
            if order_to_approve not in st.session_state.orders_table["order_id"].to_list():
                st.write(f"Could not approve order {order_to_approve} (not in the list)")
            else:
                service.approve_order(order_to_approve)
                st.write(f"Approve order {order_to_approve}")
                st.session_state.update_orders = True
    else:
        st.write("You have no unapproved orders yet")





def show_events_page():
    st.title("Events")
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants(st.session_state.id)
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant:", adresses)
    selected_restaurant_info = st.session_state.restaurants[st.session_state.restaurants["adress"] == selected_adress]
    selected_restaurant_id = selected_restaurant_info["restaurant_id"].to_list()[0]

    if ("update_events" not in st.session_state) or (st.session_state.update_events) or ("events" not in st.session_state and "last_events_update" not in st.session_state) or (st.session_state.last_events_update < (datetime.now() - timedelta(seconds=20))):
        st.session_state.events_table = CustomerService().get_events(selected_adress)
        st.session_state.last_events_update = datetime.now()
        st.session_state.update_events = False
    
    st.dataframe(st.session_state.events_table.rename(columns={"name": "Event", "date": "Date", "start_hour": "Start" , "end_hour": "End"}), hide_index=True)

    new_event = st.text_input("Event name")
    new_event_description = "Empty description" # later
    date = st.date_input("Event date", min_value=datetime.now().date())
    start_time = st.time_input("Start time")
    end_time = st.time_input("End time")

    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    duration = (end_datetime - start_datetime).total_seconds() / 60.0

    if st.button("Add event"):
        try:
            service.add_event(new_event, new_event_description, selected_restaurant_id, start_datetime, int(duration))
            st.write(f"Event {new_event} is planned to be in {selected_adress} at date {date} between {start_time} and {end_time}")
            st.session_state.update_events = True
        except:
            st.write("Something go wrong")


def main_manager():
    info = service.get_self_info(st.session_state.id)
    st.write("Welcome, ", info[0])
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select:",
        ["Approve orders", "Menu edit", "Events edit"]
    )
    if page == "Events edit":
        show_events_page()
    elif page == "Menu edit":
        show_menu_page()
    elif page == "Approve orders":
        show_orders_page()
