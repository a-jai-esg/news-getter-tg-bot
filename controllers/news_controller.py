import asyncio
import feedparser
from quart import Blueprint, jsonify, request

from controllers.ai_summarizer_controller import analyze_news

bbc_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
google_news_url = "https://news.google.com/rss/search"
request_size = 20

news_controller = Blueprint("news_controller", __name__)

@news_controller.route("/get-news", methods=["GET"])
async def news():
    query = request.args.get("q", "world")
    links = request.args.get("links", "false").lower() == "true"
    ai_summary = request.args.get("ai_summary", "false").lower() == "true"

    if query == "world":
        url = bbc_url
    else:
        query = query.replace(" ", "+")  # replace whitespace characters with (+) sign
        url = google_news_url + "?q=" + query

    # feedparser.parse is blocking; run it off the event loop.
    feed = await asyncio.to_thread(feedparser.parse, url)

    ai_summary_text = None

    # If ai_summary is requested, call analyze_news from the ai_summarizer_controller.
    if ai_summary:
        # analyze_news performs blocking I/O (OpenAI HTTP call); run it off the event loop.
        ai_summary_text = await asyncio.to_thread(analyze_news, feed.entries[:request_size])

    entries = [
        {
            "title": e.get("title"),
            "link": e.get("link") if links else None,
            "published": e.get("published"),
        }
        for e in feed.entries[:request_size]
    ]

    response = {"entries": entries}
    
    if ai_summary:
        response["ai_summary"] = ai_summary_text

    return jsonify(response)