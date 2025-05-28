# Страница аутентификации

import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib


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


# Подключение к базе данных
def create_connection():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="TW3VJywpTx",
            host="25.18.189.11",
            port="5489",
            database="postgres"
        )
        return connection
    except Error as e:
        st.error(f"Ошибка подключения к базе данных: {e}")
        return None

# Проверка логина и пароля
def check_login(username, password):
    connection = create_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor()
        
        # Хеширование пароля для сравнения
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
 
    except Error as e:
        st.error(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        if connection:
            connection.close()


# Отображение логотипа
def show_logo():
    try:
        _, col, _ = st.columns([1, 2, 1])  # Более компактная запись
        with col:
            st.image("dentistry_app/static/logo2.png",
                     width=500,
                     use_container_width='auto')
    except Exception as e:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="color: #ff6900;">Стоматологическая клиника</h1>
        </div>
        """, unsafe_allow_html=True)
        st.error(f"Ошибка загрузки логотипа: {e}")


# Основная функция страницы
def login_page():
    local_css()
    show_logo()
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
            st.session_state.update({
                'user_id': user_data[0],
                'doctor_id': user_data[1],
                'curator_id': user_data[2],
                'full_name': user_data[3],
                'current_page': 'dashboard'
            })
            st.rerun()
        else:
            st.error("Неверный логин или пароль")
    else:
        st.warning("Пожалуйста, введите логин и пароль")

if __name__ == "__main__":
    login_page()
