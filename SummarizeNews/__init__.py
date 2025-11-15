from datetime import datetime
import logging
import os
import azure.functions as func
from .util import (
    search_bring_news,
    get_openai_client,
    get_article_content,
    get_blob_container,
    ensure_container,
    get_table_client,
    sanitize_row_key,
    article_already_summarized,
    get_summary,
    upload_summary_blob,
    insert_table_entity,
    send_notification,
)


def main(mytimer: func.TimerRequest) -> None:
    logging.info("Start SummaryNews function")

    bing_key = os.getenv("BING_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
    blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
    table_conn_str = os.getenv("TABLE_CONNECTION_STRING")
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    notify_to = os.getenv("NOTIFY_TO")
    container_name = "news-summaries"
    table_name = "NewsSummaries"

    articles = search_bring_news("latest technology news", bing_key)
    if not articles:
        logging.info("No news articles found.")
        return

    openai_client = get_openai_client(openai_api_key, openai_endpoint)

    container = get_blob_container(blob_connection_string, container_name)
    ensure_container(container)

    table_client = get_table_client(table_conn_str, table_name)

    new_summaries = []

    for article in articles:
        title = article.get("name")
        link = article.get("url")
        if not title or not link:
            continue

        row_key = sanitize_row_key(link)

        if article_already_summarized(table_client, "AI_Tech", row_key):
            logging.info(f"Article already summarized: {title}")
            continue

        try:
            text = get_article_content(link)
        except Exception as e:
            logging.error(f"Failed to fetch article content: {e}")
            continue

        try:
            summary = get_summary(openai_client, text)
        except Exception as e:
            logging.error(f"OpenAI summarization failed: {e}")
            continue

        try:
            upload_summary_blob(container, title, summary, link)
            logging.info(f"✅ {title} を保存しました。")
        except Exception as e:
            logging.error(f"Failed to upload blob: {e}")
            continue

        try:
            insert_table_entity(table_client, "AI_Tech", row_key, title, link)
        except Exception as e:
            logging.error(f"Failed to write table entity: {e}")

        new_summaries.append(f"- [{title}]({link})")

    if new_summaries:
        sent = send_notification(sendgrid_api_key, notify_to, new_summaries)
        if sent:
            logging.info("📧 メール通知を送信しました。")
        else:
            logging.error("メール通知の送信に失敗しました。")
    else:
        logging.info("新規記事はありませんでした。")

    logging.info("ニュース要約処理を終了。")
