import os
import requests
import logging
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

LOGGING_FORMAT = os.getenv('ENV_LOGGING_FORMAT')

class TelegramLoggerHandler(logging.Handler):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id

    def emit(self, record):
        encoded_log_entry = urllib.parse.quote(self.format(record), safe='')
        URL = f"https://api.telegram.org/bot{os.getenv('ENV_BOT_KEY')}/sendMessage?chat_id={self.chat_id}&text={encoded_log_entry}&disable_web_page_preview=true"
        requests.get(url=URL)

def get_logger():
    logger = logging.getLogger()
    log_level = os.getenv('ENV_LOGGING_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    error_handler = TelegramLoggerHandler(os.getenv('ENV_ERROR_CHAT_ID'))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

    info_handler = TelegramLoggerHandler(os.getenv('ENV_INFO_CHAT_ID'))
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(error_handler)
    logger.addHandler(info_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger
