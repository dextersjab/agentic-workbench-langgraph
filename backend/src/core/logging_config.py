"""
Logging configuration for the application.
This module sets up dual logging to console and file.
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging with both file and console handlers
log_filename = f"logs/support_desk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create formatters and handlers
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format)

# Console handler (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    log_filename,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[console_handler, file_handler],
    force=True,
)

# Suppress noisy loggers
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)

# Log startup message
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized - writing to file: {log_filename}")
