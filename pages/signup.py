import streamlit as st
import re
from database import signup

st.set_page_config(page_title="Sign Up", page_icon="🛕")

st.title("🛕 DevaPath - Sign Up")

name = st.text_input("Full Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
confirm = st.text_input("Confirm Password", type="password")


def check_password_strength(pwd):
    """
    Password validate karta hai.
    Return: (is_valid: bool, message: str, score: int out of 5)
    """
    score = 0
    errors = []

    if len(pwd) >= 8:
        score += 1
    else:
        errors.append("Kam se kam 8 characters")

    if re.search(r"[A-Z]", pwd):
        score += 1
    else:
        errors.append("1 uppercase letter (A-Z)")

    if re.search(r"[a-z]", pwd):
        score += 1
    else:
        errors.append("1 lowercase letter (a-z)")

    if re.search(r"[0-9]", pwd):
        score += 1
    else:
        errors.append("1 number (0-9)")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\];']", pwd):
        score += 1
    else:
        errors.append("1 special character (!@#$% etc.)")

    is_valid = (score == 5)

    if is_valid:
        message = "✅ Strong Password!"
    else:
        message = "❌ Weak Password — Missing: " + ", ".join(errors)

    return is_valid, message, score


# --- Live password strength feedback ---
if password:
    is_valid, msg, score = check_password_strength(password)

    # Progress bar (0 to 1)
    st.progress(score / 5)

    if score <= 2:
        st.error(msg)
    elif score in (3, 4):
        st.warning(msg)
    else:
        st.success(msg)


if st.button("Create Account", use_container_width=True):

    if not name or not email or not password or not confirm:
        st.warning("Please fill all fields.")

    elif password != confirm:
        st.error("Passwords do not match.")

    else:
        is_valid, msg, score = check_password_strength(password)

        if not is_valid:
            st.error("Signup failed — " + msg)
        else:
            success = signup(name, email, password)

            if success:
                st.success("✅ Account created successfully!")
                st.session_state.signup_success = True
                st.switch_page("pages/login.py")

            else:
                st.error("Email already exists.")
st.divider()

if st.button("🔐 Back to Login", use_container_width=True):
    st.switch_page("pages/login.py")
