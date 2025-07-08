import streamlit as st
import yfinance as yf

def render_dashboard():
    st.set_page_config(page_title="FinanceGPT Dashboard", page_icon="📈")

    # 🌟 Page Heading
    st.markdown("""
        <h2 style="text-align:center;">🏠 <span style="color:#f97316;">Market Dashboard</span></h2>
        <p style="text-align:center;color:gray;">
            Track live stock performance • Nifty, Sensex, and major Indian equities
        </p>
        <hr style="margin-top:1rem;margin-bottom:2rem;">
    """, unsafe_allow_html=True)

    # 🧠 Predefined stocks
    tickers = {
        '^NSEI': 'Nifty 50',
        '^BSESN': 'Sensex',
        'RELIANCE.NS': 'Reliance',
        'INFY.NS': 'Infosys',
        'TCS.NS': 'TCS'
    }

    st.subheader("📊 Live Stock Metrics")

    cols = st.columns(3)

    for i, (symbol, label) in enumerate(tickers.items()):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get('regularMarketPrice', 0)
            previous = info.get('previousClose', 0)
            change = price - previous
            pct_change = (change / previous * 100) if previous else 0
            arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
            color = "#16a34a" if change > 0 else "#dc2626" if change < 0 else "#6b7280"

            # 🧱 Stylish Card Component
            with cols[i % 3]:
                st.markdown(f"""
                    <div style='padding:1.1rem;border-radius:12px;
                                background:#1e1e1e;color:white;
                                box-shadow:0 4px 10px rgba(0,0,0,0.3);
                                border-left:5px solid {color};
                                margin-bottom:1.5rem;'>
                        <div style='font-size:1.2rem;font-weight:bold;margin-bottom:0.2rem;color:#f3f4f6;'>{label}</div>
                        <div style='font-size:1.6rem;margin-bottom:0.2rem;'>₹{price}</div>
                        <div style='color:{color};font-size:1rem;'>{arrow} {change:.2f} ({pct_change:.2f}%)</div>
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            with cols[i % 3]:
                st.error(f"❌ Error loading {label}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align:center;margin-top:1.5rem;'>
            <span style='color:#60a5fa;'>📉 Data via Yahoo Finance (delayed).</span><br>
            <small style='color:gray;'>For official data, refer to NSE/BSE portals.</small>
        </div>
    """, unsafe_allow_html=True)
