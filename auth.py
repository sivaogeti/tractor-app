# auth.py
import json
import streamlit as st

def authenticate(username, password):
    users = st.secrets["users"]
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None
