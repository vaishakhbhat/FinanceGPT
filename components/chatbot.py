import streamlit as st
import httpx
import os
import yfinance as yf
from dotenv import load_dotenv


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


def get_stock_price(symbol: str) -> str:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        price = info.get("regularMarketPrice")
        if price is not None:
            return f"📈 {symbol.upper()} current price: ₹{price}"
        return f"⚠️ Price not found for {symbol.upper()}."
    except Exception as e:
        return f"❌ Error fetching stock: {str(e)}"


def get_groq_response(prompt: str) -> str:
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    model = "llama3-70b-8192"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert financial assistant that helps with stock analysis and investment advice."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = httpx.post(endpoint, headers=headers, json=payload, timeout=20.0)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error communicating with Groq: {str(e)}"


def render_chatbot():
    st.set_page_config(page_title="FinanceGPT Chat", page_icon="🤖")

    st.markdown("""
        <h2 style='text-align:center;'>💬 AI Investment Assistant</h2>
        <p style='text-align:center;color:gray;'>Powered by Groq • Get smart stock insights instantly</p>
        <hr style="margin-top:1rem;margin-bottom:2rem;">
    """, unsafe_allow_html=True)

    if not groq_api_key:
        st.error("🔐 Missing `GROQ_API_KEY` in .env file.")
        return

   
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.chat_input("Ask about a stock like 'Price of INFY' or investment advice")

    
    for msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["bot"])

    
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        # Detect stock query or general investment chat
        if "price" in user_query.lower():
            words = user_query.upper().split()
            symbols = [word for word in words if word.isalpha() and len(word) <= 5]
            response = get_stock_price(symbols[0]) if symbols else "🔍 Please mention a valid stock symbol like 'TCS' or 'INFY'."
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_groq_response(user_query)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.chat_history.append({
            "user": user_query,
            "bot": response
        })

#Launch the app
if __name__ == "__main__":
    render_chatbot()