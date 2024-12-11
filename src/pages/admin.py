import streamlit as st
from services.admin import AdminService 
from services.auth import AuthorizationService
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


service = AdminService()
auth = AuthorizationService()


def show_statistic_page():
    st.title("Statistic")
    if ("statistic_table" not in st.session_state and "last_statistic_update" not in st.session_state) or (st.session_state.last_statistic_update < datetime.now() - timedelta(minutes=1)):
        st.session_state.statistic_table = service.get_statistic()
        st.session_state.last_statistic_update = datetime.now()
    
    if st.session_state.statistic_table.shape[0] > 0:
        st.dataframe(st.session_state.statistic_table.rename(columns={"adress": "Adress", "avg_approve_time": "Approve time (min)", "total_month_income": "Monthly income"}), hide_index=True)
    else:
        st.write("No statistic info")


def show_hiring_page():
    st.title("Hiring")
    if "managers" not in st.session_state or st.session_state.managers_update:
        st.session_state.managers_table = service.get_managers()
        st.session_state.managers_update = False
    
    st.dataframe(st.session_state.managers_table.rename({"name": "Manager", "paycheck": "Paycheck", "phone": "Phone", "adresses": "Adresses"}), hide_index=True)

    new_login = st.text_input("Create login")
    new_password = st.text_input("Create password", type='password')
    name = st.text_input("Name")
    paycheck = st.number_input("Paycheck", min_value=50000, step=10000)


    if st.button("Hire manager"):
        if(auth.login(new_login, new_password)[0] != 0):
            st.write("Already registered in system")
        else:
            manager_id = auth.register_manager(new_login, new_password, name, paycheck)
            st.write(f"New manager {name} with id {manager_id}")
            st.session_state.managers_update = True
            st.rerun()


    if "restaurants" not in st.session_state:
        st.session_state.restaurants = service.get_restaurants()
    adresses = [restaurant for restaurant in st.session_state.restaurants["adress"]]
    selected_adress = st.selectbox("Select restaurant for manager:", adresses)
    selected_manager_id = st.number_input("Select manager to place", min_value=1, step=1)
    selected_restaurant_info = st.session_state.restaurants[st.session_state.restaurants["adress"] == selected_adress]
    selected_restaurant_id = selected_restaurant_info["restaurant_id"].to_list()[0]

    if st.button("Assign"):
        try:
            service.place_manager(selected_manager_id, selected_restaurant_id)
            st.write("Hire complete")
        except:
            st.write("Already working in selected restaurant")


def show_renting_page():
    st.title("Register new restaurant spot")
    if ("restaurants" not in st.session_state) or ("update_rest" not in st.session_state) or (st.session_state.update_rest):
        st.session_state.restaurants = service.get_restaurants()
        st.session_state.update_rest = False
    
    st.dataframe(st.session_state.restaurants.rename(columns={"adress": "Adress", "open_hour": "Open", "close_hour": "Close", "phone": "Phone", "email": "Email"})[["Adress", "Open", "Close", "Phone", "Email"]], hide_index=True)

    new_adress = st.text_input("Adress")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Register spot"):
        try:
            service.add_restaurant(new_adress, phone, email)
            st.write("Registration complete")
            st.session_state.update_rest = True
        except:
            st.write("Could not register")



def main_admin():
    # st.title("Who is the boss? I'm the boss!")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select:",
        ["Hiring", "Renting", "Orders statistic"]
    )
    if page == "Hiring":
        show_hiring_page()
    elif page == "Renting":
        show_renting_page()
    elif page == "Orders statistic":
        show_statistic_page() 
