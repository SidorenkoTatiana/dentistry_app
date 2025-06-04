import streamlit as st


# проверка входа в систему
def check_login():
    if 'show_control_panel' not in st.session_state:
        st.session_state.show_control_panel = False

    if 'full_name' not in st.session_state:
        st.error("Пожалуйста, войдите в систему")
        st.session_state.current_page = "login"
        st.rerun()
        return

# определение типа пользователя
def get_user_type(user_id, doctor_id, curator_id):
    if doctor_id is not None:
        return "Врач"
    elif curator_id is not None:
        return "Куратор"
    else:
        return "Неизвестный тип"


# панель управления пользователем
def user_panel():
    st.markdown("""
        <style>
            .fixed-panel {
                position: fixed;
                left: 20px;
                top: 20px;
                width: 200px;
                z-index: 1000;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .user-avatar-btn {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: #ff6900;
                color: white;
                font-weight: bold;
                font-size: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                border: none;
                cursor: pointer;
            }
        </style>
        """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'Неизвестный пользователь')
    doctor_id = st.session_state.get('doctor_id')
    curator_id = st.session_state.get('curator_id')
    user_type = get_user_type(st.session_state['user_id'], doctor_id, curator_id)

    avatar_letter = user_type[0] if user_type != "Неизвестный тип" else "U"
    
    if st.button(avatar_letter, key="avatar_button"):
        st.session_state.show_control_panel = not st.session_state.show_control_panel
        st.rerun()

    st.markdown(f"""
    <div class="user-panel">
        <div>
            <div><strong>{full_name}</strong></div>
            <div>{user_type}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.show_control_panel:
        with st.container():
            if st.button("Профиль", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()

            if st.button("На главную", use_container_width=True):
                # Определяем тип пользователя
                if curator_id:
                    st.session_state.current_page = "dashboard"
                elif doctor_id:
                    st.session_state.current_page = "schedule"
                else:
                    st.session_state.current_page = "login"
                st.rerun()

            if st.button("Выход", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.current_page = "login"
                st.rerun()


# отображение мини-логотипа справа
def mini_logo_right():
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        st.image("dentistry_app/static/logo1.png", width=70)
