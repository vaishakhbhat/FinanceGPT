import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={os.getenv('NEWS_API_KEY')}&pageSize=5&sortBy=publishedAt&language=en"
    try:
        response = requests.get(url)
        data = response.json()
        return data['articles']
    except:
        return []