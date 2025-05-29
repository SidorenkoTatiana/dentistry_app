# Панель управления
import streamlit as st
import psycopg2

# Подключение к БД
conn = psycopg2.connect(
    host="25.18.189.11",
    port="5489",
    dbname="postgres",
    user="postgres",
    password="TW3VJywpTx"
)
cursor = conn.cursor()

# CSS стили
def set_css():
    st.markdown(f"""
    <style>
        .stButton>button {{
            background-color: #ff6900;
            color: #fff;
        }}
        .user-panel {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .user-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #ff6900;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            cursor: pointer;
        }}
        .control-panel {{
            padding: 15px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }}
        .control-panel.show {{
            display: block;
        }}
        .main-content {{
            padding-left: 20px;
        }}
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 999;
            display: none;
        }}
        .overlay.show {{
            display: block;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_user_type(user_id, doctor_id, curator_id):
    """Определяем тип пользователя"""
    if doctor_id is not None:
        return "Врач"
    elif curator_id is not None:
        return "Куратор"
    else:
        return "Неизвестный тип"


def dashboard_page():
    set_css()  # Применяем CSS стили
  
    if 'show_control_panel' not in st.session_state:
        st.session_state.show_control_panel = False

    # Проверяем авторизацию
    if 'full_name' not in st.session_state:
        st.error("Пожалуйста, войдите в систему")
        st.session_state.current_page = "login"
        st.rerun()
        return
    
    # Создаем две колонки - для панели управления и основного контента
    control_col, content_col = st.columns([2, 8], gap="medium")
    
    # Панель управления в левой колонке
    with control_col:
        # Получаем данные из сессии
        full_name = st.session_state.get('full_name', 'Неизвестный пользователь')
        doctor_id = st.session_state.get('doctor_id')
        curator_id = st.session_state.get('curator_id')
        user_type = get_user_type(st.session_state['user_id'], doctor_id, curator_id)
        
        # Определяем букву для аватарки
        avatar_letter = user_type[0] if user_type != "Неизвестный тип" else "U"
        
        # Кнопка-аватар
        if st.button(avatar_letter, key="avatar_button"):
            st.session_state.show_control_panel = not st.session_state.show_control_panel
            st.rerun()
        
        # Панель пользователя
        st.markdown(f"""
        <div class="user-panel">
            <div>
                <div><strong>{full_name}</strong></div>
                <div>{user_type}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Панель управления (появляется при нажатии на аватар)
        if st.session_state.show_control_panel:
            with st.container():
                if st.button("Профиль", use_container_width=True):
                    st.session_state.current_page = "profile"
                    st.rerun()
                
                if st.button("Выход", use_container_width=True):
                    # Очищаем сессию
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.current_page = "login"
                    st.rerun()
    
    # Основной контент в правой колонке
    with content_col:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Создаем 3 колонки (левая пустая, центральная для лого, правая пустая)
        left_space, center_col, right_space = st.columns([1, 2, 1])
        
        with center_col:
            st.image("dentistry_app/static/logo2.png",
                     width=500,
                     use_container_width='auto')
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h1 style="color: #ff6900;">Меню выбора</h1>
            </div>
            """, unsafe_allow_html=True)

        with st.form("dashboard"):
            cols = st.columns(3)  # Создаем 3 равные колонки
            
            with cols[0]:  # Первая колонка
                if st.form_submit_button("Расписание"):
                    st.session_state.current_page = "schedule"
                    st.rerun()
            
            with cols[1]:  # Центральная колонка
                if st.form_submit_button("Запись на приём"):
                    st.session_state.current_page = "service"
                    st.rerun()
            
            with cols[2]:  # Последняя колонка
                if st.form_submit_button("Пациенты"):
                    st.session_state.current_page = "patient"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_page()
