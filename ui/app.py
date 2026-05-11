import streamlit as st
from sidebar import render_sidebar
from main_content import render_input_form, render_result
from history_storage import load_history
import base64

# Конфигурация страницы
st.set_page_config(layout="wide", page_title="ToT Interface")


with open("D:\\Tree_of_Thoughts\\logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{logo_base64}" style="width: 120px; margin-right: 15px;">
        <h1 style="margin: 0;">Tree of Thoughts</h1>
    </div>
    """,
    unsafe_allow_html=True
)


# Инициализация сессии
if "history" not in st.session_state:
        st.session_state.history = load_history()
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "show_viz" not in st.session_state:
    st.session_state.show_viz = False

# Боковая панель (история)
render_sidebar()

# Основная область
if st.session_state.current_result is None:
    render_input_form()
else:
    render_result()