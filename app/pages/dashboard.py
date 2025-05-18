# Панель управления

import streamlit as st


def config_page():
    st.set_page_config(
        page_title="Панель управления",
        layout="wide"
    )

def dashboard_page():
    config_page()
    
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.warning("Пожалуйста, войдите в систему")
        st.session_state.current_page = "login"
        st.experimental_rerun()
        return
    
    st.title(f"Добро пожаловать, {st.session_state.full_name}!")
    st.write("Это панель управления стоматологической клиникой.")
    
    if st.button("Выйти"):
        st.session_state.clear()
        st.session_state.current_page = "login"
        st.experimental_rerun()

if __name__ == "__main__":
    dashboard_page()

# Здесь будет основная логика панели управления
