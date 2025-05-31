# Расписание
import streamlit as st
from connection import conn, cursor
from datetime import datetime, timedelta, date
from functions import user_panel, check_login, mini_logo_right


def search_participants(participant_type, search_term):
    """Поиск участников в базе данных"""
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

def get_week_schedule(participant_id=None, participant_type=None, week_start=None):
    """Получает расписание на неделю для выбранного участника"""
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


def display_week_calendar(week_start, schedule_data):
    """Отображает расписание в виде недельного календаря"""
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    
    # Создаем таблицу с днями недели
    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            current_date = week_dates[i]
            is_today = current_date == date.today()
            day_style = "color: #1E90FF; font-weight: bold;" if is_today else ""
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px; {day_style}">
                    {days[i]}<br>
                    {current_date.strftime('%d.%m')}
                </div>
            """, unsafe_allow_html=True)
            
            # Отображаем записи для каждого дня
            day_records = [r for r in schedule_data if r[1] == current_date]
            for record in day_records:
                time = record[2].strftime('%H:%M')
                if st.session_state.participant_type == "Врач":
                    name = f"{record[7]} {record[8]} {record[9]}"
                else:
                    name = f"{record[4]} {record[5]} {record[6]}"
                
                with st.expander(f"{time} - {name}", expanded=False):
                    st.write(f"**Услуга:** {record[10]}")
                    if record[3]:
                        st.write(f"**Комментарий:** {record[3]}")



def schedule_page():
    check_login()
    
    # Инициализация состояния
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
    
    # Основной интерфейс
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h1 style="color: black;">Расписание</h1>
            </div>
            """, unsafe_allow_html=True)
        
        is_doctor = st.session_state.get('doctor_id') is not None
        
        # Инициализация состояния
        if 'current_week' not in st.session_state:
            today = date.today()
            st.session_state.current_week = today - timedelta(days=today.weekday())
        
        # Для врача сразу устанавливаем его как выбранного участника
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

        if not is_doctor:
            # Инициализация дополнительных состояний для куратора
            if 'participant_type' not in st.session_state:
                st.session_state.participant_type = "Врач"
            if 'search_query' not in st.session_state:
                st.session_state.search_query = ""
            if 'show_dropdown' not in st.session_state:
                st.session_state.show_dropdown = False
            
            # Поиск участников
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
                
                # Выпадающий список с результатами
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
        
        # Отображение выбранного участника (или врача, если пользователь - врач)
        if st.session_state.get('selected_participant'):
            if is_doctor:
                st.success(f"Ваше расписание")
            else:
                st.success(f"Выбран {st.session_state.selected_participant['type'].lower()}: {st.session_state.selected_participant['name']}")
            
            # Навигация по неделям
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

            # Получаем данные расписания
            schedule_data = get_week_schedule(
                participant_id=st.session_state.selected_participant['id'],
                participant_type=st.session_state.selected_participant['type'],
                week_start=st.session_state.current_week
            )

            # Отображаем недельное расписание
            if schedule_data:
                display_week_calendar(
                    st.session_state.current_week, 
                    schedule_data,
                    is_doctor_view=is_doctor
                )
            else:
                st.info("На выбранную неделю записей не найдено")
        elif is_doctor:
            st.error("Не удалось загрузить ваши данные. Пожалуйста, обратитесь к администратору.")


if __name__ == "__main__":
    schedule_page()
