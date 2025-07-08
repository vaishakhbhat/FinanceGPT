import streamlit as st
import os
from dotenv import load_dotenv
import requests

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_advice(income, risk_profile):
    if not GROQ_API_KEY:
        return "❌ Groq API key not found."

    prompt = (
        f"I'm an Indian investor with a monthly investment capacity of ₹{income}. "
        f"My risk profile is {risk_profile}. Please suggest a diversified asset allocation plan "
        "breaking down percentages into Equity, Debt, Emergency Fund, Gold, and other assets. "
        "Also explain why this split suits my profile in 2-3 sentences."
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

        # ✅ Gracefully handle missing or malformed responses
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            return f"❌ Groq API Error: {data['error'].get('message', 'Unknown error')}"
        else:
            return "❌ Unexpected response format from Groq."

    except Exception as e:
        return f"❌ Failed to fetch advice: {str(e)}"


def render_investment_allocator():
    st.title("📊 Smart Investment Allocator")

    salary = st.number_input("💰 Monthly Investable Amount (₹)", min_value=1000, step=1000)

    risk = st.radio("🎯 Select Your Risk Profile:", ["Conservative", "Balanced", "Aggressive"])

    if salary:
        st.subheader("📌 Suggested Allocation")

        base_alloc = {
            "Conservative": {
                "Emergency Fund": 0.3,
                "Debt Instruments": 0.4,
                "Equity": 0.2,
                "Gold": 0.1
            },
            "Balanced": {
                "Emergency Fund": 0.2,
                "Debt Instruments": 0.3,
                "Equity": 0.4,
                "Gold": 0.1
            },
            "Aggressive": {
                "Emergency Fund": 0.1,
                "Debt Instruments": 0.2,
                "Equity": 0.6,
                "Gold": 0.1
            }
        }

        alloc = base_alloc[risk]

        for asset, percent in alloc.items():
            amount = round(salary * percent)
            st.metric(label=asset, value=f"₹{amount} ({int(percent * 100)}%)")

        st.markdown("---")
        with st.expander("🧠 Ask AI for custom investment breakdown & explanation"):
            if st.button("Get AI Allocation Advice"):
                with st.spinner("Talking to Groq AI..."):
                    advice = get_groq_advice(salary, risk)
                    st.markdown(f"#### 🤖 AI says:\n\n{advice}")
