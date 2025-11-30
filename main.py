from flask import Flask, render_template, request, jsonify, send_file
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
import os
import re
import subprocess
import tempfile
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
DEVELOPMENT = os.getenv("DEVELOPMENT")
API_VERSION = os.getenv("API_VERSION")
ENDPOINT = os.getenv("ENDPOINT")
SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        news_text = data.get('news_text', '')

        if not news_text:
            return jsonify({'error': 'ニュースの本文を入力してください'}), 400

        model = AzureChatOpenAI(
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            api_key=SUBSCRIPTION_KEY,
            model_name=MODEL_NAME
        )

        template = """以下のニュース記事を要約してください。要約はMarkdown形式で出力してください。
            要約には以下の要素を含めてください：
            - タイトル（見出し1）
            - 要点（箇条書き）
            - 詳細な要約（段落形式）
            - mermaidで記事の内容を図解

            ニュース記事：
            {news_text}"""

        system_prompt = SystemMessagePromptTemplate.from_template(template)
        chain_prompt = ChatPromptTemplate.from_messages([system_prompt])

        chain = chain_prompt | model

        result = chain.invoke({"news_text": news_text})

        summary = result.content

        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        summary = data.get('summary', '')

        if not summary:
            return jsonify({'error': '要約が見つかりません'}), 400

        # Markdownファイルとしてダウンロード
        buffer = BytesIO()
        buffer.write(summary.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name='news_summary.md',
            mimetype='text/markdown'
        )

    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


if __name__ == '__main__':
    import sys
    # Azure App Service での実行に対応
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
