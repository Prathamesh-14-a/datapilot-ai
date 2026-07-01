# pages/12_ResetPassword.py
import streamlit as st
from src.database.db_connection import SessionLocal
from src.services.passwd_reset import verify_reset_token, consume_reset_token

st.set_page_config(page_title="Reset Password", page_icon="🔑")
st.title("Choose a new password")

token_value = st.query_params.get("token", "")
token = token_value[0] if isinstance(token_value, list) else token_value

if not token:
    st.error("Missing or invalid reset link.")
    st.stop()

db = SessionLocal()
try:
    rec = verify_reset_token(db, token)

    if not rec:
        st.error("This reset link is invalid or has expired. Please request a new one.")
        st.page_link("pages/11_Forget_Password.py", label="Request a new link")
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
            consume_reset_token(db, rec, pw1)
            st.success("Your password has been updated. You can now log in.")
            st.page_link("pages/1_Login.py", label="Go to login")
finally:
    db.close()

