import streamlit as st
from components.dashboard import render_dashboard
from components.stock_analysis import render_stock_analysis
from components.comparison import render_comparison
from components.portfolio import render_portfolio
from components.sentiment import render_sentiment
from components.chatbot import render_chatbot
from components.investment import render_investment_allocator
from components.premium_gate import render_payment
from components.login import login_app
from components.admin_panel import render_admin_panel

from services.db import init_db
from services.auth_db import init_user_db, get_user_profile

# --- PAGE CONFIG ---
st.set_page_config(page_title="FinanceGPT", layout="wide")

# --- DB Initialization ---
if "db_initialized" not in st.session_state:
    init_user_db()
    init_db()
    st.session_state.db_initialized = True

# --- Set default session states ---
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", None)
st.session_state.setdefault("is_premium", False)
st.session_state.setdefault("is_admin", False)

# --- Restore user data after refresh ---
if st.session_state.username and not st.session_state.logged_in:
    profile = get_user_profile(st.session_state.username)
    if profile:
        st.session_state.logged_in = True
        st.session_state.is_premium = profile["is_premium"]
        st.session_state.is_admin = profile["is_admin"]

# --- Login Flow ---
if not st.session_state.logged_in:
    if not login_app():
        st.stop()

# --- Sidebar Navigation ---
st.sidebar.title("📊 FinanceGPT Navigation")

menu_pages = [
    "🏠 Dashboard",
    "📈 Stock Analysis",
    "🔍 Compare Stocks (PRO)",
    "💼 Portfolio (PRO)",
    "📊 Investment Allocator (PRO)",
    "📰 Market Sentiment (PRO)",
    "💳 Payment Gateway",
    "🤖 AI Chatbot"
]

if st.session_state.is_admin:
    menu_pages.append("🛠️ Admin Panel")

page = st.sidebar.radio("Go to", menu_pages)

# --- Premium Page Restriction ---
premium_only = {
    "🔍 Compare Stocks (PRO)",
    "💼 Portfolio (PRO)",
    "📊 Investment Allocator (PRO)",
    "📰 Market Sentiment (PRO)"
}

if page in premium_only and not st.session_state.is_premium:
    st.warning("🚫 This feature is for premium users only. Please upgrade via Payment Gateway.")
    st.stop()

# --- Routing ---
match page:
    case "🏠 Dashboard":
        render_dashboard()
    case "📈 Stock Analysis":
        render_stock_analysis()
    case "🔍 Compare Stocks (PRO)":
        render_comparison()
    case "💼 Portfolio (PRO)":
        render_portfolio()
    case "📊 Investment Allocator (PRO)":
        render_investment_allocator()
    case "📰 Market Sentiment (PRO)":
        render_sentiment()
    case "💳 Payment Gateway":
        render_payment()
    case "🤖 AI Chatbot":
        render_chatbot()
    case "🛠️ Admin Panel" if st.session_state.is_admin:
        render_admin_panel()

# --- Logout ---
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.query_params.clear() 
    st.rerun()
