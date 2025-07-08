import streamlit as st
import yfinance as yf
import requests
import os
from dotenv import load_dotenv
from services.db import get_portfolio, add_trade, remove_trade
from services.ticker_lookup import search_ticker_options

load_dotenv()

def get_live_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.info.get("regularMarketPrice", None)
        return round(price, 2) if price else None
    except Exception as e:
        print(f"⚠️ Error fetching price for {symbol}: {e}")
        return None

def analyze_portfolio_with_groq(portfolio_rows):
    if not portfolio_rows:
        return "No portfolio data available to analyze."

    prompt = "Analyze this stock portfolio:\n\n"
    for symbol, qty, price in portfolio_rows:
        prompt += f"{symbol}: {qty} shares at ₹{price}\n"

    prompt += "\nGive me 3 insights and possible risks in bullet points."

    try:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            return "❌ GROQ_API_KEY not set in .env file"

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192", 
            "messages": [
                {"role": "system", "content": "You are a professional financial advisor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            return f"❌ Groq API error: {response.status_code} - {response.text}"

        data = response.json()
        if "choices" not in data or not data["choices"]:
            return f"❌ Groq response invalid: {data}"

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"❌ Exception: {str(e)}"


def render_portfolio():
    st.title("📊 My Stock Portfolio")

    # --- ADD STOCK SECTION ---
    with st.expander("➕ Add Stock"):
        search = st.text_input("🔍 Search NSE Stock (e.g., Infosys, TCS)")
        if search:
            options = search_ticker_options(search)
            if options:
                selected = st.selectbox("Select", options)
                symbol = selected.split(" - ")[0]

                live_price = get_live_price(symbol)
                if live_price:
                    st.success(f"💹 {symbol} Live Price: ₹{live_price}")
                    qty = st.number_input("📦 Quantity to Buy", min_value=1, step=1)
                    st.info(f"💰 Total: ₹{qty * live_price}")

                    if st.button("✅ Add to Portfolio"):
                        add_trade(symbol, qty, live_price)
                        st.success(f"✅ {symbol} added to portfolio!")
                        st.rerun()
                else:
                    st.error("❌ Couldn't fetch live price")
            else:
                st.warning("No results found")

    # --- PORTFOLIO TABLE ---
    st.markdown("---")
    st.header("📁 Portfolio Summary")

    rows = get_portfolio()
    if not rows:
        st.info("No stocks in portfolio yet.")
        return

    for symbol, total_qty, avg_price in rows:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.subheader(f"📈 {symbol}")
            st.caption(f"Quantity: {total_qty}")
            st.caption(f"Avg Buy Price: ₹{avg_price}")

        live_price = get_live_price(symbol)
        if live_price:
            pl = round((live_price - avg_price) * total_qty, 2)
            color = "green" if pl > 0 else "red" if pl < 0 else "gray"
            with col2:
                st.metric(label="💹 Live Price", value=f"₹{live_price}")
                st.markdown(f"<span style='color:{color}'>P/L: ₹{pl}</span>", unsafe_allow_html=True)

            with col3:
                sell_qty = st.number_input(f"Sell Qty ({symbol})", min_value=1, max_value=total_qty, key=symbol)
                if st.button(f"🛒 Sell {symbol}", key=symbol + "_sell"):
                    remove_trade(symbol, sell_qty)
                    st.success(f"✅ Sold {sell_qty} of {symbol}")
                    st.rerun()
        else:
            st.warning(f"⚠️ Live price not available for {symbol}")

    # --- GROQ AI ANALYZER ---
    with st.expander("🤖 Pro Insight: GPT-style Portfolio Analysis (Groq)"):
        if st.button("🔍 Analyze Portfolio"):
            with st.spinner("Thinking..."):
                analysis = analyze_portfolio_with_groq(rows)
                st.success("🧠 Here's what AI found:")
                st.markdown(analysis)

