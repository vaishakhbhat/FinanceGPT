# 💸 FinanceGPT

**FinanceGPT** is a modern, AI-powered stock analysis and portfolio management web app built with **Streamlit**. It offers NSE stock data, portfolio tracking, investment suggestions, and premium features like AI advice and smart analytics — all with a sleek, professional UI.

---

## 🚀 Features

### 🆓 Free Features:
- 📈 **Stock Analysis** — Search NSE stocks, view price charts, volume, and moving averages.
- 💳 **Payment Gateway** — Upgrade to PRO access via simulated payment.
- 🤖 **AI Chatbot** — Ask finance-related questions to an embedded GPT-powered chatbot.

### 🔒 PRO Features (after payment):
- 🔍 **Compare Stocks** — Side-by-side comparison of two NSE stocks with returns, volatility & AI insights.
- 💼 **Portfolio Tracker** — Add stocks with quantity and view auto-calculated buy values.
- 📊 **Investment Allocator** — Suggests asset allocation based on your income and risk.
- 📰 **Market Sentiment** — GPT-powered analysis of overall market mood based on stock news.

### 🔐 Authentication:
- Secure login & registration using bcrypt.
- Session-based login persists even on refresh via token in query parameters.
- Admin panel to manage users and toggle PRO access.

---

## 🧠 Powered by AI (Groq + GPT)

Uses Groq’s blazing fast API with Mixtral for:
- 🧠 **AI Investment Advice** in the Allocator
- 🧠 **Stock Comparison Insights** in Compare page

> You can switch to OpenAI GPT if needed.

---

## 🏗️ Tech Stack

| Layer        | Libraries Used                                   |
|--------------|--------------------------------------------------|
| UI           | `streamlit`, `plotly`, `streamlit-authenticator` |
| Data         | `yfinance`, `pandas`, `numpy`, `beautifulsoup4`  |
| Auth         | `bcrypt`, `sqlite3`, session tokens              |
| AI           | `requests`, `Groq API`, `langchain` (optional)   |
| DB           | `sqlite3`, `peewee` ORM                          |
| Deployment   | `GitHub`, `Streamlit Cloud`, or `Railway`        |

---

## 📦 File Structure

