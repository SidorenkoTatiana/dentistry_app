import streamlit as st

def main():
    st.set_page_config(
        page_title="Стоматологическая клиника",
        layout="wide"
    )
    
    # Инициализация session_state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'doctor_id' not in st.session_state:
        st.session_state.doctor_id = None
    if 'curator_id' not in st.session_state:
        st.session_state.curator_id = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    
    # Отображаем страницу входа по умолчанию
    from dentistry_app.app.pages.login import login_page
    login_page()

if __name__ == "__main__":
    main()