"""Centralised logging with loguru."""

import sys
from loguru import logger
from config.settings import LOG_DIR

LOG_FILE = LOG_DIR / "bot.log"

logger.remove()
logger.add(sys.stdout, colorize=True, level="INFO",
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add(LOG_FILE, rotation="10 MB", retention="14 days", level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}")

__all__ = ["logger"]
