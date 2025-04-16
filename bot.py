import requests
import time
import schedule
from telegram import Bot
from dotenv import load_dotenv
import os

# بارگذاری توکن‌ها از فایل .env
load_dotenv()

# API Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HF_API_KEY = os.getenv("HF_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY")

# API URLs
CRYPTOPANIC_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_KEY}&filter=hot"
NEWSAPI_URL = f"https://newsapi.org/v2/top-headlines?language=en&category=business&apiKey={NEWSAPI_KEY}"
HF_MODEL_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"

# Telegram Bot
bot = Bot(token=BOT_TOKEN)

# تحلیل احساسات با HuggingFace
def analyze_sentiment(text):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": text}
    response = requests.post(HF_MODEL_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['label']
    else:
        return "NEUTRAL"

# گرفتن اخبار و ارسال ترکیبی
def fetch_and_send_combined_news():
    messages = []

    # 1. CryptoPanic اخبار کریپتو (فقط 3 خبر اول)
    crypto_res = requests.get(CRYPTOPANIC_URL)
    if crypto_res.status_code == 200:
        # محدود کردن به 3 خبر اول
        for post in crypto_res.json().get("results", [])[:3]:
            title = post.get("title", "")
            url = post.get("url", "")
            domain = post.get("domain", "")
            sentiment = analyze_sentiment(title)
            msg = f"**Crypto News**\n**Source:** {domain}\n**Headline:** {title}\n[Read more]({url})\n**Impact:** {sentiment}"
            messages.append(msg)

    # 2. NewsAPI اخبار اقتصادی/سیاسی (فقط 3 خبر اول)
    news_res = requests.get(NEWSAPI_URL)
    if news_res.status_code == 200:
        # محدود کردن به 3 خبر اول
        for article in news_res.json().get("articles", [])[:3]:
            title = article.get("title", "")
            url = article.get("url", "")
            source = article.get("source", {}).get("name", "")
            sentiment = analyze_sentiment(title)
            msg = f"**Economic/Political News**\n**Source:** {source}\n**Headline:** {title}\n[Read more]({url})\n**Impact:** {sentiment}"
            messages.append(msg)

    # ارسال به تلگرام
    for msg in messages:
        bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')

# اجرای خودکار هر 20 دقیقه
schedule.every(20).minutes.do(fetch_and_send_combined_news)

print("Bot is running...")

while True:
    schedule.run_pending()
    time.sleep(1)