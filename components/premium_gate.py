import streamlit as st
from services.payment import create_checkout_session
from services.auth_db import upgrade_user_to_pro, is_user_pro

def render_payment():
    st.title("💳 Upgrade to FinanceGPT Pro")
    st.markdown("Unlock premium features like AI insights, portfolio tools, investment advisors, and more.")

    # ✅ Detect payment success via query params
    params = st.query_params

    if params.get("payment") == "success":
        st.success("🎉 Your Pro access is now active!")
        st.session_state.is_premium = True

        # Update DB permanently (requires username in session)
        if st.session_state.get("username"):
            upgrade_user_to_pro(st.session_state.username)

        st.balloons()
        return  # Avoid showing upgrade button again

    elif params.get("payment") == "cancel":
        st.warning("❌ Payment cancelled. You can try again anytime.")

    # 💳 Payment Button
    if st.button("Upgrade to Pro (₹499)"):
        checkout_url = create_checkout_session()
        st.success("✅ Redirecting to Stripe...")
        st.markdown(f"[Click here if not redirected]({checkout_url})", unsafe_allow_html=True)

    # ℹ️ Show status if already pro
    if st.session_state.get("username") and is_user_pro(st.session_state.username):
        st.session_state.is_premium = True
        st.info("✅ You're already a Pro user!")
