# pages/11_ForgotPassword.py
import streamlit as st
from src.database.db_connection import SessionLocal           # adjust import to your project
from src.database.models import User
from src.services.passwd_reset import create_reset_token
from src.services.email import send_password_reset_email

st.set_page_config(page_title="Forgot Password", page_icon="🔒")
st.title("Forgot your password?")
st.write("Enter your account email and we'll send you a reset link.")

with st.form("forgot_form"):
    email = st.text_input("Email", placeholder="you@example.com")
    submitted = st.form_submit_button("Send reset link")

if submitted:
    email_norm = (email or "").strip().lower()
    if not email_norm:
        st.error("Please enter your email.")
    else:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email_norm).first()
            if user:
                try:
                    raw_token = create_reset_token(db, user)
                    print(raw_token)
                    send_password_reset_email(user.email, raw_token)
                    print("EMAIL SENT")

                except Exception as e:
                    st.exception(e)
                    raise
            # Always show the same message (prevents email enumeration)
            st.success("If an account exists for that email, a reset link has been sent.")
        finally:
            db.close()

st.page_link("pages/1_Login.py", label="← Back to login")  # adjust filename
