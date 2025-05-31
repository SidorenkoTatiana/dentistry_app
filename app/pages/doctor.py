# Страница выбора врача (для записи на приём)
import streamlit as st
from connection import conn, cursor
from functions import check_login, user_panel, mini_logo_right


def get_doctors_for_service(service_id):
    query = """
        SELECT d.id, d.Фамилия, d.Имя, d.Отчество, s.Специальность
        FROM Врач d
        JOIN Специальность s ON s.id = d.id_специальности
        JOIN Услуга u ON s.id = u.id_специальности
        WHERE u.id = %s
        ORDER BY d.Фамилия, d.Имя
        """
    cursor.execute(query, (service_id,))
    return cursor.fetchall()


def display_doctor_card(doctor):
    with st.container():
        st.markdown(f"""
        <div style="
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
            <h3>{doctor[1]} {doctor[2]} {doctor[3] or ''}</h3>
            <p><strong>Специальность:</strong> {doctor[4]}</p>
        </div>
        """, unsafe_allow_html=True)


def doctor_page():
    check_login()

    if 'selected_service' not in st.session_state:
        st.error("Сначала выберите услугу")
        st.session_state.current_page = "service"
        st.rerun()
        return
    
    selected_service = st.session_state.selected_service
    
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.title(f"Выберите врача для услуги: {selected_service['name']}")

        doctors = get_doctors_for_service(selected_service['id'])
        
        if doctors:
            st.markdown(f"**Найдено врачей:** {len(doctors)}")

            for doctor in doctors:
                display_doctor_card(doctor)

                if st.button("Выбрать", key=f"select_doctor_{doctor[0]}"):
                    st.session_state.selected_doctor = {
                        'id': doctor[0],
                        'name': f"{doctor[1]} {doctor[2]} {doctor[3] or ''}",
                        'speciality': doctor[4]
                    }
                    st.session_state.current_page = "schedule"
                    st.session_state.schedule_mode = "create_appointment"  # Новый режим
                    st.rerun()

        else:
            st.warning("Нет доступных врачей для выбранной услуги")

if __name__ == "__main__":
    doctor_page()
