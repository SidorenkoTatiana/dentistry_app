import streamlit as st
from connection import conn, cursor
from functions import check_login, user_panel, mini_logo_right
from PIL import Image
import io


def photos_page():
    check_login()
    
    control_col, content_col = st.columns([2, 8], gap="medium")
    with control_col:
        user_panel()

    with content_col:
        mini_logo_right()
        st.subheader("Снимки пациента")

        # Проверка, выбран ли пациент
        if "selected_patient_id" not in st.session_state or st.session_state.selected_patient_id is None:
            st.warning("Сначала выберите пациента на главной странице.")
        else:
            patient_id = st.session_state.selected_patient_id

            # Загрузка изображения
            uploaded_file = st.file_uploader("Загрузите снимок", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                binary_data = uploaded_file.read()
                if st.button("Сохранить снимок"):
                    cursor.execute(
                        "INSERT INTO Снимки_пациента (id_пациента, снимок, дата) VALUES (%s, %s, NOW())",
                        (patient_id, psycopg2.Binary(binary_data))
                    )
                    conn.commit()
                    st.success("Снимок успешно сохранён!")

            st.markdown("---")
            st.write("Загруженные снимки:")

            # Вывод загруженных снимков
            cursor.execute(
                "SELECT снимок, дата FROM Снимки_пациента WHERE id_пациента = %s ORDER BY дата DESC",
                (patient_id,)
            )
            images = cursor.fetchall()

            for img_data, date in images:
                st.image(Image.open(io.BytesIO(img_data)), caption=f"Дата: {date.strftime('%d.%m.%Y %H:%M:%S')}", use_column_width=True)
                st.markdown("---")


if __name__ == "__main__":
    photos_page()
