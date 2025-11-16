import logging
import os
import azure.functions as func
from .util import (
    search_bring_news,
    get_ai_client,
    get_article_content,
    get_blob_container,
    ensure_container,
    get_summary,
    upload_summary_blob,
)
from dotenv import load_dotenv

load_dotenv()


def main(mytimer: func.TimerRequest) -> None:
    logging.info("Start SummaryNews function")

    bing_key = os.getenv("BING_API_KEY")
    api_key = os.getenv("AI_API_KEY")
    ai_endpoint = os.getenv("AI_ENDPOINT")
    blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
    container_name = os.getenv("BLOB_CONTAINER_NAME")

    articles = search_bring_news("latest technology news", bing_key)
    if not articles:
        logging.info("No news articles found.")
        return

    ai_client = get_ai_client(api_key, ai_endpoint)

    container = get_blob_container(blob_connection_string, container_name)
    ensure_container(container)

    new_summaries = []

    for article in articles:
        title = article.get("name")
        link = article.get("url")
        if not title or not link:
            continue

        try:
            text = get_article_content(link)
        except Exception as e:
            logging.error(f"Failed to fetch article content: {e}")
            continue

        try:
            summary = get_summary(ai_client, text)
        except Exception as e:
            logging.error(f"OpenAI summarization failed: {e}")
            continue

        try:
            upload_summary_blob(container, title, summary, link)
            logging.info(f"✅ {title} を保存しました。")
        except Exception as e:
            logging.error(f"Failed to upload blob: {e}")
            continue

        new_summaries.append(f"- [{title}]({link})")

    logging.info("ニュース要約処理を終了。")
