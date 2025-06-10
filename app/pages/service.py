# Страница выбора услуг (для записи на приём)
import streamlit as st
from app.connection import cursor
from app.functions import mini_logo_right, make_interface


# Получение услуг из базы данных
def get_all_services(search_query=None):
    if search_query:
        query = """
        SELECT id, Услуга
        FROM Услуга
        WHERE Услуга ILIKE %s
        ORDER BY Услуга
        """
        search_param = f"%{search_query}%"
        cursor.execute(query, (search_param,))
    else:
        query = """
        SELECT id, Услуга
        FROM Услуга
        ORDER BY Услуга
        """
        cursor.execute(query)

    return cursor.fetchall()


# Отображение карточки услуги
def display_service_card(service):
    with st.container():
        st.markdown(f"""
        <div style="
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
            <h3>{service[1]}</h3>
        </div>
        """, unsafe_allow_html=True)


# Основная функция страницы
def service_page():
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    content_col = make_interface()

    with content_col:
        mini_logo_right()
        st.title("Выберите услугу")

        search_input = st.text_input(
            "Поиск по названию услуги",
            value=st.session_state.search_query,
            key='service_search_input',
            on_change=lambda: setattr(st.session_state, 'search_query', st.session_state.service_search_input)
        )

        services = get_all_services(st.session_state.search_query if st.session_state.search_query else None)

        if services:
            st.markdown(f"**Найдено услуг:** {len(services)}")

            for service in services:
                display_service_card(service)

                if st.button("Выбрать", key=f"select_service_{service[0]}"):
                    st.session_state.selected_service = {
                        'id': service[0],
                        'name': service[1]
                    }
                    st.session_state.current_page = "doctor"
                    st.rerun()
        else:
            if st.session_state.search_query:
                st.warning("Услуги по вашему запросу не найдены")
            else:
                st.warning("В системе пока нет доступных услуг")


if __name__ == "__main__":
    service_page()
