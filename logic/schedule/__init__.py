import logging
from logging.handlers import RotatingFileHandler

from logic import configure_file_handler

rfh: RotatingFileHandler = configure_file_handler("schedule")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rfh)

logger.info("Logger initialised")
