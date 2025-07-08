import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import os
import requests
from dotenv import load_dotenv
from services.ticker_lookup import search_ticker_options

# Load Groq API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_valid_ticker(option_text):
    """Extract ticker and ensure it works with yfinance"""
    if not option_text:
        return None
    symbol = option_text.split(" - ")[0].strip()
    return symbol if symbol.endswith(".NS") else f"{symbol}.NS"

def calculate_metrics(data):
    returns = data["Close"].pct_change().dropna()
    total_return = round((data["Close"].iloc[-1] - data["Close"].iloc[0]) / data["Close"].iloc[0] * 100, 2)
    volatility = round(np.std(returns) * 100, 2)
    return total_return, volatility

def ask_groq_about_stocks(ticker1, ticker2):
    if not GROQ_API_KEY:
        return "❌ Groq API key not found."

    prompt = (
        f"Compare the Indian NSE stocks {ticker1} and {ticker2} based on their past 6-month performance, "
        "volatility, and investment suitability for Indian retail investors. Provide a short recommendation on which suits whom better."
    )
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are a professional Indian financial advisor."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 400
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Failed to get comparison: {str(e)}"

def render_comparison():
    st.title("📊 Stock Comparison Pro")
    st.markdown("Compare two NSE-listed stocks with charts, volatility, returns & AI advice.")

    col1, col2 = st.columns(2)

    with col1:
        name1 = st.text_input("🏢 First Company", placeholder="e.g., Infosys")
        options1 = search_ticker_options(name1) if name1 else []
        opt1 = st.selectbox("Select First", options1) if options1 else None

    with col2:
        name2 = st.text_input("🏢 Second Company", placeholder="e.g., Reliance")
        options2 = search_ticker_options(name2) if name2 else []
        opt2 = st.selectbox("Select Second", options2) if options2 else None

    if opt1 and opt2:
        ticker1 = get_valid_ticker(opt1)
        ticker2 = get_valid_ticker(opt2)

        try:
            data1 = yf.Ticker(ticker1).history(period="6mo")
            data2 = yf.Ticker(ticker2).history(period="6mo")
        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
            return

        if data1.empty or data2.empty:
            st.error("❌ Couldn't fetch data for one or both tickers. Try again or check symbols.")
            return

        # --- Normalized Chart ---
        st.subheader("📈 6-Month Relative Price Performance")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data1.index,
            y=data1["Close"] / data1["Close"].iloc[0],
            name=ticker1,
            line=dict(width=3)
        ))
        fig.add_trace(go.Scatter(
            x=data2.index,
            y=data2["Close"] / data2["Close"].iloc[0],
            name=ticker2,
            line=dict(width=3)
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            title="📈 Stock Performance (Normalized)",
            legend_title="Company",
            template="plotly_white",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Metrics ---
        st.subheader("📊 Analytics Summary")
        r1, v1 = calculate_metrics(data1)
        r2, v2 = calculate_metrics(data2)

        c1_name = opt1.split(" - ")[1]
        c2_name = opt2.split(" - ")[1]

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**📌 {c1_name}**")
            st.metric("Total Return", f"{r1}%", delta_color="normal")
            st.metric("Volatility", f"{v1}%")

        with colB:
            st.markdown(f"**📌 {c2_name}**")
            st.metric("Total Return", f"{r2}%", delta_color="normal")
            st.metric("Volatility", f"{v2}%")

        # --- Current Prices ---
        st.markdown("---")
        st.subheader("💰 Current Price Snapshot")

        price_col1, price_col2 = st.columns(2)
        try:
            curr1 = yf.Ticker(ticker1).info.get("regularMarketPrice", "❓")
            curr2 = yf.Ticker(ticker2).info.get("regularMarketPrice", "❓")
        except:
            curr1 = curr2 = "N/A"

        with price_col1:
            st.metric(f"{ticker1}", f"₹{curr1}")
        with price_col2:
            st.metric(f"{ticker2}", f"₹{curr2}")

        # --- Groq AI Comparison ---
        st.markdown("---")
        with st.expander("🧠 Ask AI to Compare These Stocks"):
            if st.button("Get AI Analysis"):
                with st.spinner("Consulting Groq AI..."):
                    ai_analysis = ask_groq_about_stocks(ticker1, ticker2)
                    st.markdown(f"#### 🤖 AI says:\n\n{ai_analysis}")
