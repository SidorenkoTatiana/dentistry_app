import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from app import PAGES


def main():
    st.set_page_config(
        page_title="Стоматологическая клиника",
        layout="wide"
    )

    # Инициализация состояния страницы
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"

    # Загрузка текущей страницы
    page = PAGES.get(st.session_state.current_page)
    if page:
        page()
    else:
        st.error("Страница не найдена")
        st.session_state.current_page = "login"
        st.experimental_rerun()


if __name__ == "__main__":
    main()
