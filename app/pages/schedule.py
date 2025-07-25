# Расписание с функцией записи на прием
import streamlit as st
from datetime import datetime, timedelta, date, time
from app.connection import conn, cursor
from app.functions import mini_logo_right, make_interface


# Поиск участников в базе данных
def search_participants(participant_type, search_term):
    table = "Врач" if participant_type == "Врач" else "Пациент"
    query = f"""
    SELECT id, Фамилия, Имя, Отчество
    FROM {table}
    WHERE Фамилия ILIKE %s OR Имя ILIKE %s OR Отчество ILIKE %s
    OR CONCAT(Фамилия, ' ', Имя) ILIKE %s
    OR CONCAT(Фамилия, ' ', Имя, ' ', Отчество) ILIKE %s
    ORDER BY Фамилия, Имя
    LIMIT 10
    """

    search_param = f"%{search_term}%"
    cursor.execute(query, (search_param, search_param, search_param, search_param, search_param))
    return cursor.fetchall()


# Получение расписания на неделю для выбранного участника
def get_week_schedule(participant_id=None, participant_type=None, week_start=None):
    if not participant_id or not week_start:
        return []

    week_end = week_start + timedelta(days=6)

    query = """
    SELECT
        r.id,
        r.Дата,
        r.Время,
        r.Комментарий,
        d.Фамилия as doctor_surname,
        d.Имя as doctor_name,
        d.Отчество as doctor_patronymic,
        p.Фамилия as patient_surname,
        p.Имя as patient_name,
        p.Отчество as patient_patronymic,
        s.Услуга as service_name
    FROM Расписание r
    LEFT JOIN Врач d ON r.id_врача = d.id
    LEFT JOIN Пациент p ON r.id_пациента = p.id
    LEFT JOIN Услуга s ON r.id_услуги = s.id
    WHERE r.Дата BETWEEN %s AND %s
    """

    if participant_type == "Врач":
        query += " AND r.id_врача = %s"
    else:
        query += " AND r.id_пациента = %s"

    query += " ORDER BY r.Дата, r.Время"

    cursor.execute(query, (week_start, week_end, participant_id))
    return cursor.fetchall()


# Получение доступных временных слотов для записи к врачу
def get_available_time_slots(doctor_id, date):
    work_start = time(9, 0)
    work_end = time(19, 0)

    query = """
    SELECT Время
    FROM Расписание
    WHERE id_врача = %s AND Дата = %s
    ORDER BY Время
    """
    cursor.execute(query, (doctor_id, date))
    existing_appointments = [t[0] for t in cursor.fetchall()]

    time_slots = []
    current_time = datetime.combine(date, work_start)
    end_time = datetime.combine(date, work_end)

    while current_time + timedelta(minutes=30) <= end_time:
        slot_start = current_time.time()
        slot_end = (current_time + timedelta(minutes=30)).time()

        is_available = True
        for app_time in existing_appointments:
            if slot_start <= app_time < slot_end:
                is_available = False
                break

        if is_available:
            time_slots.append(slot_start)

        current_time += timedelta(minutes=30)

    return time_slots


# Создание новой записи на прием
def create_appointment(doctor_id, patient_id, service_id, appointment_date, appointment_time, comment=None):
    query = """
    INSERT INTO Расписание (id_врача, id_пациента, id_услуги, Дата, Время, Комментарий)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    cursor.execute(query, (doctor_id, patient_id, service_id, appointment_date, appointment_time, comment))
    conn.commit()
    return cursor.fetchone()[0]


# Отображение формы для создания новой записи
def display_appointment_form(doctor_id, selected_date):
    st.subheader("Новая запись на прием")

    patient_search = st.text_input("Поиск пациента", key="patient_search")

    selected_patient = None
    if patient_search:
        patients = search_participants("Пациент", patient_search)
        if patients:
            patient_options = {f"{p[1]} {p[2]} {p[3] or ''}": p[0] for p in patients}
            patient_name = st.selectbox(
                "Выберите пациента", 
                options=list(patient_options.keys()),
                key="patient_select"
            )
            selected_patient = patient_options[patient_name]
            st.session_state.selected_patient_id = selected_patient
        else:
            st.warning("Пациенты не найдены")

    if selected_patient or st.session_state.get('selected_patient_id'):
        patient_id = selected_patient if selected_patient else st.session_state.selected_patient_id

        with st.form(key='appointment_form'):
            time_slots = get_available_time_slots(doctor_id, selected_date)

            if not time_slots:
                st.warning("Нет доступных временных слотов на выбранную дату")
                return False

            selected_time = st.selectbox(
                "Время приема",
                time_slots,
                format_func=lambda t: t.strftime('%H:%M'),
                key="time_select"
            )

            comment = st.text_area("Комментарий (необязательно)", key="comment")

            submitted = st.form_submit_button("Подтвердить запись")

            if submitted:
                try:
                    appointment_id = create_appointment(
                        doctor_id=doctor_id,
                        patient_id=patient_id,
                        service_id=st.session_state.selected_service['id'],
                        appointment_date=selected_date,
                        appointment_time=selected_time,
                        comment=comment
                    )
                    st.success(f"Запись успешно создана")
                    if 'selected_patient_id' in st.session_state:
                        del st.session_state.selected_patient_id
                    return True
                except Exception as e:
                    st.error(f"Ошибка при создании записи: {str(e)}")
                    conn.rollback()

    elif patient_search and not selected_patient:
        st.error("Пожалуйста, выберите пациента из списка")

    return False


# Отображение расписания в виде недельного календаря
def display_week_calendar(week_start, schedule_data, is_doctor_view=False):
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            current_date = week_dates[i]
            is_today = current_date == date.today()
            day_style = "color: #ff6900; font-weight: bold;" if is_today else ""
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px; {day_style}">
                    {days[i]}<br>
                    {current_date.strftime('%d.%m')}
                </div>
            """, unsafe_allow_html=True)

            day_records = [r for r in schedule_data if r[1] == current_date]
            if day_records:
                for record in day_records:
                    time_str = record[2].strftime('%H:%M')
                    doctor_name = f"{record[4]} {record[5]} {record[6] or ''}"
                    patient_name = f"{record[7]} {record[8]} {record[9] or ''}"
                    service_name = record[10]
                    comment = record[3]
                    with st.expander(f"{time_str}", expanded=False):
                        st.write(f"**Услуга:** {service_name}")
                        st.write(f"**Врач:** {doctor_name}")
                        st.write(f"**Пациент:** {patient_name}")
                        if comment:
                            st.write(f"**Комментарий:** {comment}")
            else:
                st.info("Нет записей")

            if st.session_state.get('schedule_mode') == "create_appointment" and not is_doctor_view:
                if st.button("Добавить запись", key=f"add_appointment_{i}"):
                    st.session_state['appointment_date'] = current_date
                    st.session_state['show_appointment_form'] = True
                    st.rerun()


# Основная функция страницы
def schedule_page():

    if 'participant_type' not in st.session_state:
        st.session_state.participant_type = "Врач"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'selected_participant' not in st.session_state:
        st.session_state.selected_participant = None
    if 'show_dropdown' not in st.session_state:
        st.session_state.show_dropdown = False
    if 'current_week' not in st.session_state:
        today = date.today()
        st.session_state.current_week = today - timedelta(days=today.weekday())
    if 'show_appointment_form' not in st.session_state:
        st.session_state.show_appointment_form = False

    content_col = make_interface()

    with content_col:
        mini_logo_right()
        st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h1 style="color: black;">Расписание</h1>
            </div>
            """, unsafe_allow_html=True)

        is_doctor = st.session_state.get('doctor_id') is not None

        if is_doctor and 'selected_participant' not in st.session_state:
            cursor.execute("SELECT id, Фамилия, Имя, Отчество FROM Врач WHERE id = %s", 
                           (st.session_state['doctor_id'],))
            doctor = cursor.fetchone()
            if doctor:
                st.session_state.selected_participant = {
                    'id': doctor[0],
                    'type': "Врач",
                    'name': f"{doctor[1]} {doctor[2]} {doctor[3] or ''}"
                }

        if st.session_state.get('schedule_mode') == "create_appointment" and 'selected_doctor' in st.session_state:
            st.session_state.selected_participant = {
                'id': st.session_state.selected_doctor['id'],
                'type': "Врач",
                'name': st.session_state.selected_doctor['name']
            }
        
        if not is_doctor:
            if 'participant_type' not in st.session_state:
                st.session_state.participant_type = "Врач"
            if 'search_query' not in st.session_state:
                st.session_state.search_query = ""
            if 'show_dropdown' not in st.session_state:
                st.session_state.show_dropdown = False

            left_col, right_col = st.columns([1, 1], gap="medium")
            with left_col:
                participant_type = st.selectbox(
                    "Участник",
                    ("Пациент", "Врач"),
                    key='participant_type_select',
                    on_change=lambda: [
                        setattr(st.session_state, 'selected_participant', None),
                        setattr(st.session_state, 'search_query', ""),
                        setattr(st.session_state, 'show_dropdown', False)
                    ])

            with right_col:
                search_input = st.text_input(
                    "Введите имя участника для поиска",
                    key='search_input',
                    value=st.session_state.search_query,
                    on_change=lambda: [
                        setattr(st.session_state, 'search_query', st.session_state.search_input),
                        setattr(st.session_state, 'show_dropdown', len(st.session_state.search_input) > 2)
                    ])

                if st.session_state.show_dropdown and st.session_state.search_query:
                    st.session_state.search_results = search_participants(
                        st.session_state.participant_type_select,
                        st.session_state.search_query
                    )

                    if st.session_state.search_results:
                        with st.expander("Результаты поиска", expanded=True):
                            for person in st.session_state.search_results:
                                full_name = f"{person[1]} {person[2]} {person[3] or ''}"
                                if st.button(full_name):
                                    st.session_state.selected_participant = {
                                        'id': person[0],
                                        'type': participant_type,
                                        'name': full_name
                                    }
                                    st.session_state.search_query = full_name
                                    st.session_state.show_dropdown = False
                                    st.rerun()
                    else:
                        st.info("Ничего не найдено")
        if st.session_state.get('selected_participant'):
            if is_doctor:
                st.success(f"Ваше расписание")
            else:
                st.success(f"Выбран {st.session_state.selected_participant['type'].lower()}: {st.session_state.selected_participant['name']}")

            if st.session_state.get('schedule_mode') == "create_appointment" and 'selected_service' in st.session_state:
                st.info(f"Услуга: {st.session_state.selected_service['name']}")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Предыдущая неделя"):
                    st.session_state.current_week -= timedelta(days=7)
                    st.rerun()
            with col2:
                week_range = f"{st.session_state.current_week.strftime('%d.%m.%Y')} - {(st.session_state.current_week + timedelta(days=6)).strftime('%d.%m.%Y')}"
                st.markdown(f"**Неделя:** {week_range}", unsafe_allow_html=True)
            with col3:
                if st.button("Следующая неделя ▶"):
                    st.session_state.current_week += timedelta(days=7)
                    st.rerun()

            schedule_data = get_week_schedule(
                participant_id=st.session_state.selected_participant['id'],
                participant_type=st.session_state.selected_participant['type'],
                week_start=st.session_state.current_week
            )

            if st.session_state.get('show_appointment_form'):
                if display_appointment_form(
                    doctor_id=st.session_state.selected_participant['id'],
                    selected_date=st.session_state.get('appointment_date')
                ):
                    st.session_state.show_appointment_form = False
                    st.session_state.schedule_mode = None
                    if 'selected_service' in st.session_state:
                        del st.session_state.selected_service
                    if 'selected_doctor' in st.session_state:
                        del st.session_state.selected_doctor
                    st.rerun()

                if st.button("Отмена"):
                    st.session_state.show_appointment_form = False
                    st.rerun()
            display_week_calendar(
                st.session_state.current_week, 
                schedule_data,
                is_doctor_view=is_doctor
            )
        elif is_doctor:
            try:
                cursor.execute("""
                    SELECT Фамилия, Имя, Отчество 
                    FROM Врач 
                    WHERE id = %s
                """, (st.session_state['doctor_id'],))
                doctor_data = cursor.fetchone()

                if doctor_data:
                    last_name, first_name, patronymic = doctor_data
                    doctor_name = f"{last_name} {first_name} {patronymic or ''}".strip()
                    st.success(f"Добро пожаловать, доктор {doctor_name}!")

                    st.session_state.selected_participant = {
                        'id': st.session_state['doctor_id'],
                        'type': "Врач",
                        'name': doctor_name
                    }
                    st.rerun()
                else:
                    st.error("Ваш профиль не найден в системе")
                    
            except Exception as e:
                st.error(f"Ошибка при загрузке вашего профиля: {str(e)}")


if __name__ == "__main__":
    schedule_page()
