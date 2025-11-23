import logging
import sys
from main import app

# ロギング設定
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Flask application for Azure App Service")
    app.run(host='0.0.0.0', port=8000)
