# pages/12_ResetPassword.py
import streamlit as st
from src.database.db_connection import SessionLocal           # adjust import
from services.passwd_reset import verify_reset_token, consume_reset_token

st.set_page_config(page_title="Reset Password", page_icon="🔑")
st.title("Choose a new password")

# Streamlit ≥1.30: st.query_params
token = st.query_params.get("token", "")

if not token:
    st.error("Missing or invalid reset link.")
    st.stop()

db = SessionLocal()
rec = verify_reset_token(db, token)

if not rec:
    db.close()
    st.error("This reset link is invalid or has expired. Please request a new one.")
    st.page_link("pages/4_ForgotPassword.py", label="Request a new link")
    st.stop()

with st.form("reset_form"):
    pw1 = st.text_input("New password", type="password")
    pw2 = st.text_input("Confirm new password", type="password")
    submitted = st.form_submit_button("Update password")

if submitted:
    if len(pw1) < 8:
        st.error("Password must be at least 8 characters.")
    elif pw1 != pw2:
        st.error("Passwords do not match.")
    else:
        try:
            consume_reset_token(db, rec, pw1)
            st.success("Your password has been updated. You can now log in.")
            st.page_link("pages/1_Login.py", label="Go to login")
        finally:
            db.close()
