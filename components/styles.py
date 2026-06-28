from pathlib import Path
import streamlit as st

def load_global_styles():
    css = Path("assets/css/mobile.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)