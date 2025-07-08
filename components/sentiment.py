import streamlit as st
import os
import openai
from dotenv import load_dotenv
from services.news_api import fetch_news  # Your service should return list of dicts

# Load Groq API Key
load_dotenv()
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"

# Summarization via Groq LLM
def analyze_overall_sentiment(articles: list) -> str:
    combined_text = "\n\n".join(
        f"Title: {a['title']}\nDescription: {a.get('description') or a.get('content') or ''}"
        for a in articles
    )

    prompt = (
        "You're an AI financial analyst. Analyze the following market news articles.\n\n"
        "Summarize the overall situation in 2 sentences.\n"
        "Then state the overall sentiment as Positive, Negative, or Neutral.\n"
        "Finally, give a 1-line investment suggestion like: 'Consider investing' or 'Avoid for now'.\n\n"
        f"{combined_text}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

# Modern UI function
def render_sentiment():
    st.set_page_config(page_title="Market Sentiment", page_icon="📈")

    st.markdown("""
        <h2 style="text-align:center;">📊 <span style='color:#f97316;'>Market Outlook from News</span></h2>
        <p style="text-align:center;color:gray;">Powered by <b>Groq + GPT</b> • AI-generated sentiment & suggestions</p>
        <hr style="margin-top:1rem;margin-bottom:2rem;">
    """, unsafe_allow_html=True)

    stock = st.text_input("🔍 Enter company, sector, or keyword:", placeholder="e.g., Infosys, Banking, IT")

    if stock:
        with st.spinner(f"📡 Fetching news related to '{stock}'..."):
            articles = fetch_news(stock)

        if not articles:
            st.warning("🚫 No relevant news found. Try another keyword.")
            return

        st.subheader("🗞️ Top 3 News Headlines")
        for idx, article in enumerate(articles[:3], 1):
            st.markdown(f"**{idx}. [{article['title']}]({article['url']})**")
            st.caption(f"📰 {article['source']['name']} | 🕒 {article['publishedAt']}")
            st.write(article.get("description") or article.get("content") or "*No content available.*")
            st.markdown("<hr>", unsafe_allow_html=True)

        st.subheader("🤖 AI Insight & Investment Suggestion")

        with st.spinner("🧠 Analyzing sentiment like a financial analyst..."):
            summary = analyze_overall_sentiment(articles)

        # 🎨 Dynamic coloring
        lower = summary.lower()
        if "positive" in lower:
            color = "#16a34a"
        elif "negative" in lower:
            color = "#dc2626"
        elif "neutral" in lower:
            color = "#f59e0b"
        else:
            color = "#6b7280"

        # 🧱 Modern dark-mode card
        st.markdown(f"""
            <div style='padding:1.3rem;margin-top:1rem;border-radius:10px;
                        background:#1f2937;border-left:6px solid {color};
                        color:white;font-size:1rem;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3);'>
                <b>{summary}</b>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📌 These are AI-based suggestions. Always cross-check with expert advice.")
