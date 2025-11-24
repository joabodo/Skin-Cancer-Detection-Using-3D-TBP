import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = os.getenv("LOG_FILE", "/app/logs/backend.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("skinapp")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
