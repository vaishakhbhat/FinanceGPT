import streamlit as st
from services.auth_db import (
    init_user_db,
    register_user,
    authenticate_user,
    is_user_pro,
    create_user_session,
    get_username_from_token
)

def login_app():
    #Restore login from URL token
    session_token = st.query_params.get("session")
    if session_token and not st.session_state.get("logged_in"):
        username = get_username_from_token(session_token)
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.is_premium = is_user_pro(username)
            st.session_state.is_admin = (username == "admin")
            return True

    #Initialize DB
    if "db_initialized" not in st.session_state:
        init_user_db()
        st.session_state.db_initialized = True

    #Set session defaults
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("is_premium", False)
    st.session_state.setdefault("is_admin", False)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("User Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("✅ Login successful!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_premium = is_user_pro(username)
                st.session_state.is_admin = (username == "admin")

                #Generate and persist token
                token = create_user_session(username)

                #Use new query param setter (requires Streamlit 1.35+)
                st.query_params.update({"session": token})

                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    with tab2:
        st.subheader("Register New Account")
        name = st.text_input("Full Name", key="register_name")
        reg_username = st.text_input("New Username", key="register_username")
        reg_password = st.text_input("New Password", type="password", key="register_password")

        if st.button("Register"):
            if not reg_username or not reg_password or not name:
                st.warning("Please fill out all fields.")
            elif register_user(name, reg_username, reg_password):
                st.success("🎉 Account created successfully! Please login.")
            else:
                st.error("❌ Username already exists.")

    return st.session_state.logged_in
