import streamlit as st
from app.connection import conn, cursor
from app.functions import mini_logo_right, make_interface
from PIL import Image
import io


# Основная функция страницы
def photos_page():
    content_col = make_interface()

    with content_col:
        mini_logo_right()
        st.subheader("Снимки пациента")

        if "selected_patient_id" not in st.session_state or st.session_state.selected_patient_id is None:
            st.warning("Сначала выберите пациента на главной странице.")
        else:
            patient_id = st.session_state.selected_patient_id

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

            cursor.execute(
                "SELECT снимок, дата FROM Снимки_пациента WHERE id_пациента = %s ORDER BY дата DESC",
                (patient_id,)
            )
            images = cursor.fetchall()

            for img_data, date in images:
                st.image(Image.open(io.BytesIO(img_data)), caption=f"Дата: {date.strftime('%d.%m.%Y %H:%M:%S')}", use_column_width=True)
                st.markdown("---")

            if st.button("Вернуться"):
                st.session_state.current_page = "patient"
                st.rerun()


if __name__ == "__main__":
    photos_page()
