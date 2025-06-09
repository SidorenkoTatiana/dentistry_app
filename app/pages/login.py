# Страница аутентификации

import streamlit as st
import hashlib
from app.connection import cursor


# CSS стили
def local_css():
    st.markdown(f"""
    <style>
        .stButton>button {{
            background-color: #ff6900;
            color: #fff;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
        }}
        .stButton>button:hover {{
            background-color: #ff6900;
            color: #fff;
        }}
        .stTextInput>div>div>input {{
            padding: 0.5rem;
        }}
        .logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)


# Проверка логина и пароля
def check_login(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("""
        SELECT a.id, a.id_Врача, a.id_Куратора,
                COALESCE(d.Фамилия || ' ' || d.Имя || ' ' || d.Отчество, k.Фамилия || ' ' || k.Имя || ' ' || k.Отчество) as full_name
        FROM Аутентификатор a
        LEFT JOIN Врач d ON a.id_Врача = d.id
        LEFT JOIN Куратор k ON a.id_Куратора = k.id
        WHERE a.Логин = %s AND a.Пароль = %s
    """, (username, hashed_password))

    result = cursor.fetchone()
    return result


# Основная функция страницы
def login_page():
    local_css()
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.image("dentistry_app/static/logo2.png",
                 width=500,
                 use_container_width='auto')
    st.title("Вход в систему")

    with st.form("login_form"):
        username = st.text_input("Логин", key="username")
        password = st.text_input("Пароль", type="password", key="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Вход"):
                handle_login(username, password)
        with col2:
            if st.form_submit_button("Регистрация"):
                st.session_state.current_page = "registration"
                st.rerun()


# Обработка входа
def handle_login(username, password):
    if username and password:
        user_data = check_login(username, password)
        if user_data:
            is_doctor = user_data[1] is not None

            st.session_state.update({
                'user_id': user_data[0],
                'doctor_id': user_data[1],
                'curator_id': user_data[2],
                'full_name': user_data[3],
                'current_page': 'schedule' if is_doctor else 'dashboard'
            })
            st.rerun()
        else:
            st.error("Неверный логин или пароль")
    else:
        st.warning("Пожалуйста, введите логин и пароль")


if __name__ == "__main__":
    login_page()
