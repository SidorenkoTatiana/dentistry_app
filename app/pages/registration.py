import streamlit as st


def config_page():
    st.set_page_config(
        page_title="Регистрация",
        layout="centered"
    )


def registration_page():
    config_page()
    st.title("Регистрация")
    st.write("Здесь будет форма регистрации новых пользователей.")

    if st.button("Вернуться к входу"):
        st.session_state.current_page = "login"
        st.experimental_rerun()


if __name__ == "__main__":
    registration_page()
