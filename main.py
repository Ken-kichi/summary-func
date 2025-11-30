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
            return jsonify({'error': 'Please enter the full news article text.'}), 400

        model = AzureChatOpenAI(
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            api_key=SUBSCRIPTION_KEY,
            model_name=MODEL_NAME
        )

        template = """Summarize the following news article in Markdown format.
            Include the elements below in your response:
            - Title (Heading 1)
            - Key points (bullet list)
            - Detailed summary (paragraph form)
            - A Mermaid diagram that illustrates the article

            News article:
            {news_text}"""

        system_prompt = SystemMessagePromptTemplate.from_template(template)
        chain_prompt = ChatPromptTemplate.from_messages([system_prompt])

        chain = chain_prompt | model

        result = chain.invoke({"news_text": news_text})

        summary = result.content

        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        summary = data.get('summary', '')

        if not summary:
            return jsonify({'error': 'Summary not found.'}), 400

        # Download as a Markdown file
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
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    import sys
    # Support execution on Azure App Service
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
