import streamlit as st
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
import os
import yfinance as yf
from dotenv import load_dotenv

# Load .env keys
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Stock fetch logic
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

# Chat page
def render_chatbot():
    st.set_page_config(page_title="FinanceGPT Chat", page_icon="🤖")

    st.markdown("""
        <h2 style='text-align:center;'>💬 AI Investment Assistant</h2>
        <p style='text-align:center;color:gray;'>Powered by Groq • Get smart stock insights instantly</p>
        <hr style="margin-top:1rem;margin-bottom:2rem;">
    """, unsafe_allow_html=True)

    if not groq_api_key:
        st.error("🔐 Missing `GROQ_API_KEY` in .env")
        return

    # Init LangChain Groq LLM
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192"  # ✅ Use supported Groq model
    )

    tools = [
        Tool(
            name="Stock Price Tool",
            func=get_stock_price,
            description="Use this to get real-time NSE/BSE stock prices."
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )

    # Session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Native Streamlit chat input (Streamlit 1.25+)
    user_query = st.chat_input("Ask something like 'Should I invest in Infosys?'")

    # Display past messages
    for msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["bot"])

    # On new query
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent.run(user_query)
                except Exception as e:
                    response = f"❌ Error: {str(e)}"
            st.markdown(response)

        # Save to history
        st.session_state.chat_history.append({
            "user": user_query,
            "bot": response
        })
