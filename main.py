"""
Main entry point for the agentic workflows API.
"""
import dotenv
import logging
import logging.handlers
import os
from datetime import datetime
from langchain.globals import set_debug, set_verbose
from src.core.api import app

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
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[console_handler, file_handler],
    force=True
)

logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_filename}")


if __name__ == "__main__":
    logger.info("Starting agentic workflows API server")

    # Load environment variables
    dotenv.load_dotenv()
    
    # Enable LangChain debugging
    set_debug(True)
    set_verbose(True)
    
    # TODO add configuration from environment variables?
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
    )
