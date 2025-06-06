import streamlit as st
from connection import conn, cursor
from functions import check_login, user_panel, mini_logo_right


def patient_page():
    check_login()

    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.title("Пациенты")

        with st.expander("➕ Добавить пациента"):
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
                try:
                    cursor.execute("""
                        INSERT INTO Пациент 
                        (Фамилия, Имя, Отчество, Дата_рождения, Номер_телефона, СНИЛС, ОМС, ДМС, Паспорт) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (surname, name, patronymic, birth_date, phone, snils, oms, dms, passport))
                    conn.commit()
                    st.success("Пациент добавлен")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Ошибка при добавлении пациента: {e}")

        search = st.text_input("Поиск по ФИО или телефону").strip()
        words = search.split()

        try:
            if search:
                if len(words) == 1:
                    pattern = f"%{words[0]}%"
                    cursor.execute("""
                        SELECT * FROM Пациент
                        WHERE Фамилия ILIKE %s OR Имя ILIKE %s OR Отчество ILIKE %s OR Номер_телефона ILIKE %s
                    """, (pattern, pattern, pattern, pattern))

                elif len(words) == 2:
                    pattern1 = f"%{words[0]}%"
                    pattern2 = f"%{words[1]}%"
                    cursor.execute("""
                        SELECT * FROM Пациент
                        WHERE (Фамилия ILIKE %s AND Имя ILIKE %s)
                           OR (Имя ILIKE %s AND Отчество ILIKE %s)
                    """, (pattern1, pattern2, pattern1, pattern2))

                elif len(words) >= 3:
                    pattern1 = f"%{words[0]}%"
                    pattern2 = f"%{words[1]}%"
                    pattern3 = f"%{words[2]}%"
                    cursor.execute("""
                        SELECT * FROM Пациент
                        WHERE Фамилия ILIKE %s AND Имя ILIKE %s AND Отчество ILIKE %s
                    """, (pattern1, pattern2, pattern3))
            else:
                cursor.execute("SELECT * FROM Пациент")
        except Exception as e:
            conn.rollback()
            st.error(f"Ошибка при поиске: {e}")
            cursor.execute("SELECT * FROM Пациент")  # fallback

        rows = cursor.fetchall()

        if "selected_patient_id" not in st.session_state:
            st.session_state.selected_patient_id = None

        st.subheader("⬇ Список пациентов")
        for row in rows:
            st.write(f"{row[0]}: {row[1]} {row[2]} {row[3]}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Выбрать {row[1]}", key=f"select_{row[0]}"):
                    st.session_state.selected_patient_id = row[0]
                    st.rerun()
            with col2:
                if st.button(f"Удалить {row[1]}", key=f"delete_{row[0]}"):
                    try:
                        cursor.execute("DELETE FROM Пациент WHERE id = %s", (row[0],))
                        conn.commit()
                        st.warning(f"Пациент {row[1]} удалён")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Ошибка при удалении пациента: {e}")

        if st.session_state.selected_patient_id:
            st.success(f"Выбран пациент: {row[1]} {row[2]} {row[3]}")
            if st.button("Перейти в медкарту"):
                st.session_state.current_page = "medcart"
                st.rerun()
            if st.button("Перейти к снимкам"):
                st.session_state.current_page = "photos"
                st.rerun()

if __name__ == "__main__":
    patient_page()