import streamlit as st

from src.config.paths import ASSETS_DIR


def load_global_styles():
    css = (ASSETS_DIR / "css" / "mobile.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)