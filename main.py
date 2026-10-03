import asyncio
import sys

import feedparser
from dotenv import load_dotenv
from quart import Quart, jsonify, request
from quart_cors import cors

load_dotenv()

app = Quart(__name__)
cors(app, allow_origin="*")

bbc_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
google_news_url = "https://news.google.com/rss/search"
request_size = 20


@app.route("/get-news", methods=["GET"])
async def news():
    query = request.args.get("q", "world")
    if query == "world":
        url = bbc_url
    else:
        query = query.replace(" ", "+") # replace whitespace characters with (+) sign
        url = google_news_url + "?q=" + query

    # feedparser.parse is blocking; run it off the event loop.
    feed = await asyncio.to_thread(feedparser.parse, url)

    return jsonify([
        {
            "title": e.get("title"),
            "link": e.get("link"),
            "published": e.get("published"),
        }
        for e in feed.entries[:request_size]
    ])

@app.route("/get-news-titles", methods=["GET"])
async def news_titles():
    query = request.args.get("q", "world")
    if query == "world":
        url = bbc_url
    else:
        query = query.replace(" ", "+") # replace whitespace characters with (+) sign
        url = google_news_url + "?q=" + query

    # feedparser.parse is blocking; run it off the event loop.
    feed = await asyncio.to_thread(feedparser.parse, url)

    return jsonify([
        {
            "title": e.get("title"),
            "published": e.get("published"),
        }
        for e in feed.entries[:request_size]
    ])


if __name__ == "__main__":
    # Local development only.
    # Production: gunicorn main:app (see gunicorn.conf.py)
    try:
        app.run(debug=False)
        print("News API catcher is running.")
    except Exception as e:
        sys.stderr.write(f"News API catcher failed to start: {e}\n")
