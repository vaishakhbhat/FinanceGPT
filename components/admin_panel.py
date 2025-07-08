import streamlit as st
import sqlite3
from services.auth_db import upgrade_user_to_pro, revoke_user_pro

def render_admin_panel():
    st.title("🛠️ Admin - User Management")

    # Fetch all users
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT id, username, name, pro_access FROM users")
    users = cur.fetchall()
    conn.close()

    st.markdown("### 👥 Registered Users")

    for uid, username, name, pro in users:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            with col1:
                st.markdown(f"**{name}** (`{username}`)")
            with col2:
                st.markdown(f"**Pro:** {'✅ Yes' if pro == 'yes' else '❌ No'}")
            with col3:
                if pro != 'yes':
                    if st.button("Grant Pro", key=f"grant_{uid}"):
                        upgrade_user_to_pro(username)
                        st.success(f"✅ {username} is now Pro!")
                        st.rerun()
            with col4:
                if pro == 'yes':
                    if st.button("Revoke Pro", key=f"revoke_{uid}"):
                        revoke_user_pro(username)
                        st.warning(f"❌ {username}'s Pro access revoked.")
                        st.rerun()
