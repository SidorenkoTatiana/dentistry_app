import streamlit as st
from connection import conn, cursor
from functions import check_login, user_panel, mini_logo_right


def medcart_page():
    check_login()
    
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.subheader("Медкарта пациента")

        # Проверка, выбран ли пациент
        if "selected_patient_id" not in st.session_state or st.session_state.selected_patient_id is None:
            st.warning("Сначала выберите пациента на главной странице.")
        else:
            patient_id = st.session_state.selected_patient_id

            # Получение данных пациента
            cursor.execute("SELECT Фамилия, Имя, Отчество FROM Пациент WHERE id = %s", (patient_id,))
            p = cursor.fetchone()
            st.write(f"Пациент: {p[0]} {p[1]} {p[2]}")

            # Получение текущей медкарты
            cursor.execute("SELECT id, История_болезни FROM Мед_карта_пациента WHERE id_пациента = %s", (patient_id,))
            card = cursor.fetchone()

            # Отображение/редактирование
            history_text = st.text_area("История болезни", value=card[1] if card else "", height=300)

            col_1, col_2 = st.columns([1, 1])
            with col_1:
                if st.button("Сохранить медкарту"):
                    if card:
                        cursor.execute(
                            "UPDATE Мед_карта_пациента SET История_болезни = %s WHERE id = %s",
                            (history_text, card[0])
                        )
                        st.success("Медкарта обновлена.")
                    else:
                        cursor.execute(
                            "INSERT INTO Мед_карта_пациента (id_пациента, История_болезни) VALUES (%s, %s)",
                            (patient_id, history_text)
                        )
                        st.success("Медкарта добавлена.")
                    conn.commit()
            with col_2:
                if st.button("Вернуться"):
                    st.session_state.current_page = "patient"
                    st.rerun()


if __name__ == "__main__":
    medcart_page()
