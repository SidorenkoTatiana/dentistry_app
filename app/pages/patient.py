import streamlit as st
import datetime
from app.connection import conn, cursor
from app.functions import mini_logo_right, make_interface


def patient_page():
    content_col = make_interface()

    with content_col:
        mini_logo_right()
        st.title("Пациенты")

        with st.expander("➕ Добавить пациента"):
            surname = st.text_input("Фамилия*", value="")
            name = st.text_input("Имя*", value="")
            patronymic = st.text_input("Отчество", value="")
            birth_date = st.date_input("Дата рождения*", 
                                      min_value=datetime.date(1900, 1, 1), 
                                      max_value=datetime.date.today())
            phone = st.text_input("Номер телефона", value="")
            snils = st.text_input("СНИЛС*", value="")
            oms = st.text_input("ОМС*", value="")
            dms = st.text_input("ДМС", value="")
            passport = st.text_input("Паспорт*", value="")

            st.markdown("<sup>*</sup> Обязательные поля", unsafe_allow_html=True)

            if st.button("Добавить пациента"):
                # Проверка обязательных полей с явным приведением типов
                if (not surname.strip() or not name.strip() or 
                    birth_date is None or 
                    not snils.strip() or not oms.strip() or 
                    not passport.strip()):
                    st.error("Пожалуйста, заполните все обязательные поля (помеченные *)")
                else:
                    try:
                        cursor.execute("""
                            INSERT INTO Пациент 
                            (Фамилия, Имя, Отчество, Дата_рождения, Номер_телефона, СНИЛС, ОМС, ДМС, Паспорт) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            surname.strip(),
                            name.strip(),
                            patronymic.strip() if patronymic else None,
                            birth_date,
                            phone.strip() if phone else None,
                            snils.strip(),
                            oms.strip(),
                            dms.strip() if dms else None,
                            passport.strip()
                        ))
                        conn.commit()
                        st.success("Пациент добавлен")
                        st.rerun()
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
            cursor.execute("SELECT * FROM Пациент")

        rows = cursor.fetchall()

        if "selected_patient_id" not in st.session_state:
            st.session_state.selected_patient_id = None

        st.subheader("⬇ Список пациентов")
        for row in rows:
            st.write(f"{row[1]} {row[2]} {row[3]}")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button(f"Выбрать: {row[1]}", key=f"select_{row[0]}"):
                    st.session_state.selected_patient_id = row[0]
                    st.rerun()
            
            with col2:
                if st.button(f"Редактировать: {row[1]}", key=f"edit_{row[0]}"):
                    st.session_state.editing_patient_id = row[0]
                    st.session_state.editing_patient_data = {
                        "surname": row[1],
                        "name": row[2],
                        "patronymic": row[3],
                        "birth_date": row[4],
                        "phone": row[5],
                        "snils": row[7],
                        "oms": row[8],
                        "dms": row[9],
                        "passport": row[6]
                    }
                    st.rerun()
            
            with col3:
                if st.button(f"Удалить: {row[1]}", key=f"delete_{row[0]}"):
                    try:
                        cursor.execute("DELETE FROM Пациент WHERE id = %s", (row[0],))
                        conn.commit()
                        st.warning(f"Пациент {row[1]} удалён")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Ошибка при удалении пациента: {e}")

        if "editing_patient_id" in st.session_state:
            with st.expander(f"✏️ Редактирование пациента {st.session_state.editing_patient_data['surname']}", expanded=True):
                edited_surname = st.text_input("Фамилия*", value=st.session_state.editing_patient_data["surname"])
                edited_name = st.text_input("Имя*", value=st.session_state.editing_patient_data["name"])
                edited_patronymic = st.text_input("Отчество", value=st.session_state.editing_patient_data["patronymic"])
                edited_birth_date = st.date_input("Дата рождения*", 
                                                value=st.session_state.editing_patient_data["birth_date"],
                                                min_value=datetime.date(1900, 1, 1), 
                                                max_value=datetime.date.today())
                edited_phone = st.text_input("Номер телефона", value=st.session_state.editing_patient_data["phone"])
                edited_snils = st.text_input("СНИЛС*", value=st.session_state.editing_patient_data["snils"])
                edited_oms = st.text_input("ОМС*", value=st.session_state.editing_patient_data["oms"])
                edited_dms = st.text_input("ДМС", value=st.session_state.editing_patient_data["dms"])
                edited_passport = st.text_input("Паспорт*", value=st.session_state.editing_patient_data["passport"])

                st.markdown("<sup>*</sup> Обязательные поля", unsafe_allow_html=True)

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Сохранить изменения"):
                        if (not edited_surname.strip() or not edited_name.strip() or 
                            edited_birth_date is None or 
                            not edited_snils.strip() or not edited_oms.strip() or 
                            not edited_passport.strip()):
                            st.error("Пожалуйста, заполните все обязательные поля (помеченные *)")
                        else:
                            try:
                                cursor.execute("""
                                    UPDATE Пациент SET
                                    Фамилия = %s,
                                    Имя = %s,
                                    Отчество = %s,
                                    Дата_рождения = %s,
                                    Номер_телефона = %s,
                                    СНИЛС = %s,
                                    ОМС = %s,
                                    ДМС = %s,
                                    Паспорт = %s
                                    WHERE id = %s
                                """, (
                                    edited_surname.strip(),
                                    edited_name.strip(),
                                    edited_patronymic.strip() if edited_patronymic else None,
                                    edited_birth_date,
                                    edited_phone.strip() if edited_phone else None,
                                    edited_snils.strip(),
                                    edited_oms.strip(),
                                    edited_dms.strip() if edited_dms else None,
                                    edited_passport.strip(),
                                    st.session_state.editing_patient_id
                                ))
                                conn.commit()
                                st.success("Данные пациента обновлены")
                                del st.session_state.editing_patient_id
                                del st.session_state.editing_patient_data
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Ошибка при обновлении данных: {e}")
                
                with col_cancel:
                    if st.button("Отмена"):
                        del st.session_state.editing_patient_id
                        del st.session_state.editing_patient_data
                        st.rerun()

        if st.session_state.selected_patient_id:
            selected_patient = next((row for row in rows if row[0] == st.session_state.selected_patient_id), None)
            if selected_patient:
                st.success(f"Выбран пациент: {selected_patient[1]} {selected_patient[2]} {selected_patient[3]}")
                if st.button("Перейти в медкарту"):
                    st.session_state.current_page = "medcart"
                    st.rerun()
                if st.button("Перейти к снимкам"):
                    st.session_state.current_page = "photos"
                    st.rerun()


if __name__ == "__main__":
    patient_page()