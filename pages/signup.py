import streamlit as st
from database import signup

st.set_page_config(page_title="Sign Up", page_icon="🛕")

st.title("🛕 DevaPath - Sign Up")

name = st.text_input("Full Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
confirm = st.text_input("Confirm Password", type="password")

if st.button("Create Account", use_container_width=True):

    if not name or not email or not password or not confirm:
        st.warning("Please fill all fields.")

    elif password != confirm:
        st.error("Passwords do not match.")

    else:

        success = signup(name, email, password)

        if success:
            st.success("✅ Account created successfully!")
            st.session_state.signup_success = True
            st.info("Now go to Login page.")

        else:
            st.error("Email already exists.")