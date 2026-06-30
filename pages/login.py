import streamlit as st
from database import login

st.set_page_config(
    page_title="Login",
    page_icon="🛕",
    layout="centered"
)

# Agar pehle se login hai to seedha app par bhejo
if st.session_state.get("logged_in", False):
    st.switch_page("app.py")

st.title("🛕 DevaPath")
st.subheader("Login to Continue")

# Signup ke baad success message
if "signup_success" in st.session_state:
    st.success("🎉 Account Created Successfully. Please Login.")
    del st.session_state["signup_success"]

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("🔐 Login", use_container_width=True):

    if not email or not password:
        st.warning("Please enter Email and Password.")

    else:
        user = login(email, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.email = user[2]

            st.success(f"Welcome {user[1]}!")
            st.switch_page("app.py")

        else:
            st.error("❌ Invalid Email or Password")

st.divider()

st.write("Don't have an account?")

if st.button("📝 Create New Account", use_container_width=True):
    st.switch_page("pages/Signup.py")