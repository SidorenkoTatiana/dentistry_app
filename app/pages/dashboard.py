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
            position: fixed;
            top: 20px;
            left: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
        .user-menu {{
            position: absolute;
            top: 60px;
            left: 0;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 4px;
            padding: 10px;
            z-index: 1001;
            width: 150px;
        }}
        .main-content {{
            margin-top: 100px;
            padding: 20px;
        }}
        .logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
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

def show_logo():
    try:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.image("dentistry_app/static/logo2.png",
                    width=500,
                    use_container_width='auto')
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="color: #ff6900;">Стоматологическая клиника</h1>
        </div>
        """, unsafe_allow_html=True)
        st.error(f"Ошибка загрузки логотипа: {e}")


def dashboard_page():
    set_css()  # Применяем CSS стили
    
    # Инициализация состояния меню
    if 'show_user_menu' not in st.session_state:
        st.session_state.show_user_menu = False
    
    # Проверяем авторизацию
    if 'full_name' not in st.session_state:
        st.error("Пожалуйста, войдите в систему")
        st.session_state.current_page = "login"
        st.rerun()
        return
    
    # Получаем данные из сессии
    full_name = st.session_state.get('full_name', 'Неизвестный пользователь')
    doctor_id = st.session_state.get('doctor_id')
    curator_id = st.session_state.get('curator_id')
    user_type = get_user_type(st.session_state['user_id'], doctor_id, curator_id)
    
    # Определяем букву для аватарки
    avatar_letter = user_type[0] if user_type != "Неизвестный тип" else "U"
    # Панель пользователя (фиксированная позиция)
    st.markdown(f"""
    <div class="user-panel">
        <div class="user-avatar" onclick="window.streamlitApi.runMethod('toggle_menu')">{avatar_letter}</div>
        <div>
            <div><strong>{full_name}</strong></div>
            <div>{user_type}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Обработка клика по аватару
    if st.session_state.get('toggle_menu'):
        st.session_state.show_user_menu = not st.session_state.show_user_menu
        st.session_state.toggle_menu = False
        st.rerun()
    
    # Выпадающее меню
    if st.session_state.show_user_menu:
        st.markdown("""
        <div class="user-menu">
            <button onclick="window.streamlitApi.runMethod('profile_clicked')" class="stButton">Профиль</button>
            <button onclick="window.streamlitApi.runMethod('logout_clicked')" class="stButton">Выход</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Основное содержимое
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    show_logo()
    st.write("Выберите действие")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Обработка действий меню
    if st.session_state.get('profile_clicked'):
        st.session_state.profile_clicked = False
        st.session_state.current_page = "profile"
        st.rerun()
    
    if st.session_state.get('logout_clicked'):
        st.session_state.logout_clicked = False
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.current_page = "login"
        st.rerun()


if __name__ == "__main__":
    dashboard_page()