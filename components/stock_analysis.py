import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from services.ticker_lookup import search_ticker_options

def get_valid_ticker(option_text):
    """Extract ticker and ensure it ends with .NS"""
    if not option_text:
        return None
    symbol = option_text.split(" - ")[0].strip()
    return symbol if symbol.endswith(".NS") else f"{symbol}.NS"

def render_stock_analysis():
    st.title("📈 Detailed Stock Analysis")

    name_input = st.text_input("🔍 Search NSE Company", placeholder="e.g., Infosys, Tata, Reliance")

    if name_input:
        options = search_ticker_options(name_input)
        if not options:
            st.error("❌ No matching NSE stock found. Try a different name.")
            return

        selected = st.selectbox("✅ Select a company from results", options)
        symbol = get_valid_ticker(selected)

        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            if not info or 'regularMarketPrice' not in info:
                st.error("❌ Could not retrieve stock data. Try another.")
                return

            # --- Overview Section ---
            st.subheader(f"📄 {info.get('longName', symbol)} ({symbol})")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💹 Current Price", f"₹{info.get('regularMarketPrice', 'N/A')}")
                st.write(f"**Market Cap:** ₹{info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), (int, float)) else "N/A")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")

            with col2:
                st.metric("📊 PE Ratio", f"{info.get('trailingPE', 'N/A')}")
                low_52 = info.get('fiftyTwoWeekLow', 0)
                high_52 = info.get('fiftyTwoWeekHigh', 0)
                st.metric("📈 52-Week Range", f"₹{low_52} - ₹{high_52}")

            # --- Historical Chart ---
            hist = stock.history(period="6mo")
            if hist.empty:
                st.warning("⚠️ No historical data found for this stock.")
                return

            st.markdown("### 📉 Candlestick Chart (6 Months)")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=symbol
            ))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                title=f"{symbol} - 6 Month Candlestick",
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"🚨 Unexpected error: {e}")
