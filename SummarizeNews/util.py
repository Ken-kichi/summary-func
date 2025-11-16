import datetime
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.data.tables import TableServiceClient


def search_bring_news(query: str, bing_key: Optional[str]) -> Optional[list[dict]]:
    if not bing_key:
        logging.error("Bing API key is not set.")
        return None
    url = f"https://api.bing.microsoft.com/v7.0/news/search?q={query}&mkt=ja-JP&sortBy=Date"
    headers = {"Ocp-Apim-Subscription-Key": bing_key}
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    articles = res.json().get("value", [])[:5]

    if not articles:
        logging.info("記事が見つかりませんでした。")
        return None

    return articles


def get_ai_client(api_key: str, endpoint: str,) -> OpenAI:
    client = OpenAI(
        base_url=f"{endpoint}",
        api_key=api_key
    )
    return client


def get_blob_container(blob_connection_string: str, container_name: str) -> ContainerClient:
    blob_service = BlobServiceClient.from_connection_string(
        blob_connection_string)
    container = blob_service.get_container_client(container_name)
    return container


def ensure_container(container: ContainerClient) -> None:
    try:
        container.create_container()
    except Exception:
        # container may already exist — ignore
        pass


def get_table_client(table_conn_str: str, table_name: str):
    table_service = TableServiceClient.from_connection_string(
        conn_str=table_conn_str)
    try:
        table_service.create_table_if_not_exists(table_name)
    except Exception:
        pass
    return table_service.get_table_client(table_name)


def get_article_content(link: str) -> str:
    html = requests.get(link, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    text = "\n".join(p.get_text() for p in soup.find_all("p"))
    return text


def get_summary(openai_client: OpenAI, content: str) -> str:
    # use the attached deployment name if present
    model_name = getattr(openai_client, "_deployment_name", "gpt-5-mini")
    prompt = f"Please summarize the following article into three paragraphs in Markdown format.\n\n{content[:8000]}"
    response = openai_client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    summary = response.choices[0].message.content
    return summary


def upload_summary_blob(container: ContainerClient, title: str, summary: str, link: str) -> str:
    filename = f"{datetime.datetime.now():%Y%m%d_%H%M%S}_{title[:30]}.md"
    blob_client = container.get_blob_client(filename)
    content = f"# {title}\n\n{summary}\n\n[記事URL]({link})"
    blob_client.upload_blob(content, overwrite=True)
    return filename
