"""
Main entry point for the agentic workflows API.
"""
import dotenv
import logging
from langchain_core.globals import set_debug, set_verbose

# Import logging configuration (sets up file and console logging)
from src.core import logging_config

from src.core.api import app

logger = logging.getLogger(__name__)


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
