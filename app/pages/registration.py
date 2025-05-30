# Страница регистрации

import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib
from functions import mini_logo_right


conn = psycopg2.connect(
    host="25.18.189.11",
    port="5489",
    dbname="postgres",
    user="postgres",
    password="TW3VJywpTx"
)
cursor = conn.cursor()


def registration_page():
    left_col, right_col = st.columns([1, 1], gap="medium")
    with left_col:
        st.title("Регистрация")
    with right_col:
        mini_logo_right()

    user_type = st.selectbox("Тип пользователя", ("Куратор", "Врач"))
    surname = st.text_input("Фамилия")
    name = st.text_input("Имя")
    patronymic = st.text_input("Отчество")
    phone = st.text_input("Номер телефона")
    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Регистрация"):
        if user_type == "Куратор":
            cursor.execute(
                """
                INSERT INTO Куратор (Фамилия, Имя, Отчество, Номер_телефона)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (surname, name, patronymic, phone)
            )

            curator_id = cursor.fetchone()[0]

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                """
                INSERT INTO Аутентификатор (Логин, Пароль, id_Куратора)
                VALUES (%s, %s, %s)
                """,
                (login, hashed_password, curator_id)
            )

        if user_type == "Врач":
            cursor.execute(
                """
                INSERT INTO Врач (Фамилия, Имя, Отчество, Номер_телефона)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (surname, name, patronymic, phone)
            )

            doctor_id = cursor.fetchone()[0]

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                """
                INSERT INTO Аутентификатор (Логин, Пароль, id_Врача)
                VALUES (%s, %s, %s)
                """,
                (login, hashed_password, doctor_id)
            )

        conn.commit()
        st.session_state.current_page = "login"
        st.rerun()

    if st.button("Вернуться к входу"):
        st.session_state.current_page = "login"
        st.rerun()


if __name__ == "__main__":
    registration_page()
