# Страница управления пользователем
import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib


conn = psycopg2.connect(
    host="25.18.189.11",
    port="5489",
    dbname="postgres",
    user="postgres",
    password="TW3VJywpTx"
)
cursor = conn.cursor()


def profile_page():
    st.title("Профиль")


if __name__ == "__main__":
    profile_page()
