from services.auth import AuthorizationService
from pages.customer import main_customer
from pages.manager import main_manager
from pages.admin import main_admin
import pandas as pd
import numpy as np
import streamlit as st


service = AuthorizationService()


def register_user():
    new_login = st.text_input("Create login")
    new_password = st.text_input("Create password", type='password')
    name = st.text_input("Name")
    phone = st.text_input("Phone (like +7 XXX XXX-XX-XX)")
    if st.button("Sign up"):
        if(service.login(new_login, new_password)[0] != 0):
            st.write("Already registered, go to sign in page")
        else:
           st.session_state.id = service.register_customer(new_login, new_password, name, phone)

def login_user():
    login = st.text_input("Login")
    password = st.text_input("Password", type='password')
    if st.button("Sign in"):
        if "account" not in st.session_state or  not st.session_state.account[0] > 0:
            st.session_state.account = service.login(login, password)
        role = "customer"
        if st.session_state.account[0] == 0:
            st.write("No such login, go to sign up page")
        elif st.session_state.account[0] == -1:
            st.write("Wrong password, try again")
        else:
            st.session_state.id = st.session_state.account[0]
            if st.session_state.account[1] == 1:
                role = "manager"
            elif st.session_state.account[1] == 2:
                role = "admin"
        return role



if __name__ == "__main__":
    if "id" not in st.session_state:
        st.session_state.role = "customer"
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Select:",
            ["Sign in", "Sign up"]
        )
        if page == "Sign in":
            st.session_state.role = login_user()
        elif page == "Sign up":
            register_user()
    else:
        if st.session_state.role == "customer":
            main_customer()
        elif st.session_state.role == "manager":
            main_manager()
        elif st.session_state.role == "admin":
            main_admin()
