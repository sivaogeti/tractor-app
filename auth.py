# auth.py
import json
import streamlit as st

USERS = {
    "employee1": {"password": "pass123", "role": "employee"},
    "employee2": {"password": "pass456", "role": "employee"},
    "admin": {"password": "admin123", "role": "admin"},
}

def authenticate(username, password):
    users = st.secrets["users"]
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None
