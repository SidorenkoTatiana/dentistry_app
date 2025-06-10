# Панель управления
import streamlit as st
from app.functions import make_interface


# Основная функция страницы
def dashboard_page():
    content_col = make_interface()

    with content_col:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        _, center_col, _ = st.columns([1, 2, 1])

        with center_col:
            st.image("dentistry_app/static/logo2.png",
                     width=600,
                     use_container_width='auto')
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h1 style="color: black;">Меню выбора</h1>
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
