from flask import Flask, render_template
import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

RSS_FEEDS = {
    "Banking": "https://news.google.com/rss/search?q=banking+current+affairs&hl=en-IN&gl=IN&ceid=IN:en",
    "RBI": "https://news.google.com/rss/search?q=RBI&hl=en-IN&gl=IN&ceid=IN:en",
    "SBI": "https://news.google.com/rss/search?q=State+Bank+of+India&hl=en-IN&gl=IN&ceid=IN:en",
    "Finance": "https://news.google.com/rss/search?q=finance+economy+India&hl=en-IN&gl=IN&ceid=IN:en"
}

def fetch_detailed_summary(url, word_limit=200):
    """Fetch the news page and return first ~200 words of text."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract all paragraph texts
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()  # clean extra spaces

        words = text.split()
        if len(words) > word_limit:
            text = " ".join(words[:word_limit]) + "..."
        return text
    except Exception as e:
        print(f"Error fetching summary for {url}: {e}")
        return ""

@app.route("/")
def home():
    all_news = {}
    headers = {"User-Agent": "Mozilla/5.0"}

    for category, url in RSS_FEEDS.items():
        category_news = []
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:5]:
                published = getattr(entry, 'published', '')
                if published:
                    published = datetime(*entry.published_parsed[:6]).strftime('%d %b %Y %H:%M')

                # Fetch detailed summary from actual page
                summary_text = fetch_detailed_summary(entry.link, word_limit=200)

                news_item = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": published,
                    "summary": summary_text
                }
                category_news.append(news_item)
        except Exception as e:
            print(f"Error fetching {category}: {e}")
        all_news[category] = category_news

    return render_template("index.html", news=all_news)

if __name__ == "__main__":
    app.run(debug=True)
