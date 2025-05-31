import streamlit as st
from connection import conn, cursor
from functions import user_panel, check_login


def patient_page():
    # set_css()
    check_login()
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        st.subheader("Добавить пациента")

        # Форма для ввода всех данных
        surname = st.text_input("Фамилия")
        name = st.text_input("Имя")
        patronymic = st.text_input("Отчество")
        birth_date = st.date_input("Дата рождения")
        phone = st.text_input("Номер телефона")
        snils = st.text_input("СНИЛС")
        oms = st.text_input("ОМС")
        dms = st.text_input("ДМС")
        passport = st.text_input("Паспорт")

        if st.button("Добавить пациента"):
            cursor.execute(
                """
                INSERT INTO Пациент 
                (Фамилия, Имя, Отчество, Дата_рождения, Номер_телефона, СНИЛС, ОМС, ДМС, Паспорт)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (surname, name, patronymic, birth_date, phone, snils, oms, dms, passport)
            )
            conn.commit()
            st.success("Пациент добавлен")

        st.subheader("Поиск")
        search = st.text_input("Введите имя пациента для поиска")
        cursor.execute("SELECT * FROM Пациент WHERE Имя ILIKE %s", ('%' + search + '%',))
        rows = cursor.fetchall()

        st.subheader("Пациенты")

        if "selected_patient_id" not in st.session_state:
            st.session_state.selected_patient_id = None

        for row in rows:

            st.write(f"{row[0]}: {row[2]} {row[1]} {row[3]}")
            if st.button(f"Выбрать {row[2]}", key=f"select_{row[0]}"):
                st.session_state.selected_patient_id = row[0]
                st.rerun()
            if st.button(f"Удалить {row[2]}", key=f"delete_{row[0]}"):
                cursor.execute("DELETE FROM Пациент WHERE id = %s", (row[0],))
                conn.commit()
                st.warning(f"Пациент {row[2]} удалён")
                st.rerun()

        st.subheader("Данные выбранного пациента")
        if st.session_state.selected_patient_id is not None:
            cursor.execute("SELECT * FROM Пациент WHERE id = %s", (st.session_state.selected_patient_id,))
            patient = cursor.fetchone()
            if patient:
                st.write(f"ID: {patient[0]}")
                st.write(f"Фамилия: {patient[1]}")
                st.write(f"Имя: {patient[2]}")
                st.write(f"Отчество: {patient[3]}")
                st.write(f"Дата рождения: {patient[4]}")
                st.write(f"Номер телефона: {patient[5]}")
                st.write(f"СНИЛС: {patient[6]}")
                st.write(f"ОМС: {patient[7]}")
                st.write(f"ДМС: {patient[8]}")
                st.write(f"Паспорт: {patient[9]}")
            else:
                st.write("Пациент не найден.")
        else:
            st.write("Пациент не выбран.")

    if __name__ == "__main__":
        patient_page()
