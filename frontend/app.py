import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from frontend.api_client import APIClient
from frontend.components.auth import show_auth_page
from frontend.components.detect import show_detect_page
from frontend.components.history import show_history_page

st.set_page_config(
    page_title="Vehicle Detector",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()

api_client = st.session_state["api_client"]

if "auth_token" not in st.session_state or st.session_state["auth_token"] is None:
    show_auth_page(api_client)
else:
    with st.sidebar:
        st.success(f"Пользователь: {st.session_state.get('username', '')}")
        if st.button("Выйти"):
            keys_to_remove = ["auth_token", "username", "user_id"]
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    tabs = st.tabs(["🔍 Детекция", "📜 История"])

    with tabs[0]:
        show_detect_page(api_client)

    with tabs[1]:
        show_history_page(api_client)