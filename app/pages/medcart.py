import streamlit as st
from app.connection import conn, cursor
from app.functions import mini_logo_right, make_interface


# Основная функция страницы
def medcart_page():
    content_col = make_interface()

    with content_col:
        mini_logo_right()
        st.subheader("Медкарта пациента")

        if "selected_patient_id" not in st.session_state or st.session_state.selected_patient_id is None:
            st.warning("Сначала выберите пациента на главной странице")
        else:
            patient_id = st.session_state.selected_patient_id

            cursor.execute("SELECT Фамилия, Имя, Отчество FROM Пациент WHERE id = %s", (patient_id,))
            p = cursor.fetchone()
            st.write(f"Пациент: {p[0]} {p[1]} {p[2]}")

            cursor.execute("SELECT id, История_болезни FROM Мед_карта_пациента WHERE id_пациента = %s", (patient_id,))
            card = cursor.fetchone()

            history_text = st.text_area("История болезни", value=card[1] if card else "", height=300)

            col_1, col_2 = st.columns([1, 1])
            with col_1:
                if st.button("Сохранить медкарту"):
                    if card:
                        cursor.execute(
                            "UPDATE Мед_карта_пациента SET История_болезни = %s WHERE id = %s",
                            (history_text, card[0])
                        )
                        st.success("Медкарта обновлена")
                    else:
                        cursor.execute(
                            "INSERT INTO Мед_карта_пациента (id_пациента, История_болезни) VALUES (%s, %s)",
                            (patient_id, history_text)
                        )
                        st.success("Медкарта добавлена")
                    conn.commit()
            with col_2:
                if st.button("Вернуться"):
                    st.session_state.current_page = "patient"
                    st.rerun()


if __name__ == "__main__":
    medcart_page()
