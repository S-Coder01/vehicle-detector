import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from frontend.api_client import APIClient

def show_auth_page(api_client: APIClient):
    st.title("Вход / Регистрация")

    tab1, tab2 = st.tabs(["Вход", "Регистрация"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти")
            if submitted:
                try:
                    token = api_client.login(username, password)
                    api_client.set_token(token)
                    # Получаем информацию о пользователе
                    user_info = api_client.get_user_info()
                    st.session_state["auth_token"] = token
                    st.session_state["user_id"] = user_info["id"]
                    st.session_state["username"] = user_info["username"]
                    st.success("Вход выполнен!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка входа: {str(e)}")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Новое имя пользователя")
            new_password = st.text_input("Пароль (минимум 6 символов)", type="password")
            submitted = st.form_submit_button("Зарегистрироваться")
            if submitted:
                try:
                    api_client.register(new_username, new_password)
                    st.success("Регистрация успешна! Теперь войдите.")
                except Exception as e:
                    st.error(f"Ошибка регистрации: {str(e)}")