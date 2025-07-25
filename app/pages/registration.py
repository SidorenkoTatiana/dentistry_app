# Страница регистрации

import streamlit as st
import hashlib
from app.connection import conn, cursor
from app.functions import mini_logo_right


# Основная функция страницы
def registration_page():
    left_col, right_col = st.columns([1, 1], gap="medium")
    with left_col:
        st.title("Регистрация")
    with right_col:
        mini_logo_right()

    user_type = st.selectbox("Тип пользователя*", ("Куратор", "Врач"))
    surname = st.text_input("Фамилия*")
    name = st.text_input("Имя*")
    patronymic = st.text_input("Отчество")
    phone = st.text_input("Номер телефона")
    login = st.text_input("Логин*")
    password = st.text_input("Пароль*", type="password")

    st.markdown("<sup>*</sup> Обязательные поля", unsafe_allow_html=True)

    if st.button("Регистрация"):
        # Проверка заполнения обязательных полей
        if not surname or not name or not login or not password:
            st.error("Пожалуйста, заполните все обязательные поля (помеченные *)")
            return

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