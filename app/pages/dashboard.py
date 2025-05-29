# Панель управления
import streamlit as st
import psycopg2
from functious import user_panel, check_login

# Подключение к БД
conn = psycopg2.connect(
    host="25.18.189.11",
    port="5489",
    dbname="postgres",
    user="postgres",
    password="TW3VJywpTx"
)
cursor = conn.cursor()

def set_css():
    st.markdown("""
    <style>
        .main-content {
            margin-left: 250px;
            padding: 20px;
        }
        .stButton>button {
            background-color: #ff6900;
            color: #fff;
        }
    </style>
    """, unsafe_allow_html=True)

def dashboard_page():
    set_css()
    check_login()
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        left_space, center_col, right_space = st.columns([1, 2, 1])
        
        with center_col:
            st.image("dentistry_app/static/logo2.png",
                     width=500,
                     use_container_width='auto')
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h1 style="color: #ff6900;">Меню выбора</h1>
            </div>
            """, unsafe_allow_html=True)

        with st.form("dashboard"):
            cols = st.columns(3)
            
            with cols[0]:
                if st.form_submit_button("Расписание"):
                    st.session_state.current_page = "schedule"
                    st.rerun()
            
            with cols[1]:
                if st.form_submit_button("Запись на приём"):
                    st.session_state.current_page = "service"
                    st.rerun()
            
            with cols[2]:
                if st.form_submit_button("Пациенты"):
                    st.session_state.current_page = "patient"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    dashboard_page()