# Страница управления пользователем
import streamlit as st
from connection import conn, cursor
from psycopg2 import Error
from functions import user_panel, check_login, mini_logo_right


# Загрузка данных пользователя
def load_user_data():
    if st.session_state.get('doctor_id'):
        cursor.execute(
            """
            SELECT 'Врач' as user_type, Фамилия, Имя, Отчество, Номер_телефона
            FROM Врач 
            WHERE id = %s
            """,
            (st.session_state['doctor_id'],))
    else:
        cursor.execute(
            """
            SELECT 'Куратор' as user_type, Фамилия, Имя, Отчество, Номер_телефона
            FROM Куратор 
            WHERE id = %s
            """,
            (st.session_state['curator_id'],))

    return cursor.fetchone()


# Сохранение изменений
def save_changes(surname, name, patronymic, phone):
    if st.session_state.get('doctor_id'):
        cursor.execute(
            """
            UPDATE Врач 
            SET Фамилия = %s, Имя = %s, Отчество = %s, Номер_телефона = %s
            WHERE id = %s
            """,
            (surname, name, patronymic, phone, st.session_state['doctor_id']))
    else:
        cursor.execute(
            """
            UPDATE Куратор 
            SET Фамилия = %s, Имя = %s, Отчество = %s, Номер_телефона = %s
            WHERE id = %s
            """,
            (surname, name, patronymic, phone, st.session_state['curator_id']))

    conn.commit()
    st.success("Изменения сохранены успешно!")
    st.session_state.full_name = f"{surname} {name} {patronymic}"
    return True


def profile_page():
    check_login()
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.title("Профиль пользователя")

        user_data = load_user_data()
        if not user_data:
            st.error("Не удалось загрузить данные пользователя")
            return

        with st.form("profile_form"):
            st.markdown("### Редактирование профиля")

            user_type = st.text_input("Тип пользователя", value=user_data[0], disabled=True)
            surname = st.text_input("Фамилия*", value=user_data[1])
            name = st.text_input("Имя*", value=user_data[2])
            patronymic = st.text_input("Отчество", value=user_data[3])
            phone = st.text_input("Номер телефона*", value=user_data[4])

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Сохранить изменения")
            with col2:
                cancel = st.form_submit_button("Назад")

            if submitted:
                if not all([surname, name, phone]):
                    st.error("Пожалуйста, заполните обязательные поля (помеченные *)")
                else:
                    if save_changes(surname, name, patronymic, phone):
                        st.rerun()
            # Подумать над кнопкой назад
            if cancel:
                st.session_state.current_page = st.session_state.get('previous_page', 'dashboard')
                st.rerun()

if __name__ == "__main__":
    profile_page()
