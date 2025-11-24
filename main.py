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


@app.route('/extract-mermaid', methods=['POST'])
def extract_mermaid():
    try:
        data = request.json
        summary = data.get('summary', '')

        if not summary:
            return jsonify({'error': '要約が見つかりません'}), 400

        # Markdownからmermaidコードブロックを抽出
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(mermaid_pattern, summary, re.DOTALL)

        if not matches:
            return jsonify({'error': 'mermaid図解が見つかりません'}), 400

        return jsonify({'mermaid_diagrams': matches, 'count': len(matches)})

    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


@app.route('/convert-mermaid-png', methods=['POST'])
def convert_mermaid_png():
    """
    Mermaidコードを PNG に変換
    ※ Azure App Service では mmdc が利用できないため、ブラウザ側で処理することを推奨
    """
    try:
        import shutil

        data = request.json
        mermaid_code = data.get('mermaid_code', '')
        diagram_index = data.get('diagram_index', 0)

        if not mermaid_code:
            return jsonify({'error': 'mermaidコードが見つかりません'}), 400

        # mmdc コマンドが利用可能か確認
        mmdc_path = shutil.which('mmdc')
        if not mmdc_path:
            return jsonify({
                'error': 'Mermaid CLI がこの環境では利用できません。ローカル環境でのみ使用可能です。',
                'available_on_local': True,
                'mermaid_code': mermaid_code
            }), 501  # Not Implemented

        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            mmd_file = f.name

        try:
            # mmdc (mermaid-cli) を使用してPNGに変換
            png_file = mmd_file.replace('.mmd', '.png')
            subprocess.run(
                ['mmdc', '-i', mmd_file, '-o', png_file, '-s', '2'],
                check=True,
                capture_output=True,
                timeout=30
            )

            # PNGファイルを読み込んでバイナリで返す
            with open(png_file, 'rb') as f:
                png_data = f.read()

            buffer = BytesIO(png_data)
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'diagram_{diagram_index + 1}.png'
            )

        finally:
            # 一時ファイルをクリーンアップ
            if os.path.exists(mmd_file):
                os.remove(mmd_file)
            if os.path.exists(png_file):
                os.remove(png_file)

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'mermaid変換エラー: {e.stderr.decode() if e.stderr else str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


if __name__ == '__main__':
    import sys
    # Azure App Service での実行に対応
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
