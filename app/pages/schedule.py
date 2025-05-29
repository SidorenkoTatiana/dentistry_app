# Расписание
import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib
from functious import user_panel, check_login


conn = psycopg2.connect(
    host="25.18.189.11",
    port="5489",
    dbname="postgres",
    user="postgres",
    password="TW3VJywpTx"
)
cursor = conn.cursor()


def schedule_page():
    # set_css()
    check_login()
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        st.title("Расписание")


if __name__ == "__main__":
    schedule_page()
