"""
Main entry point for the HelpHub API server.

TODO for participants: Add configuration management,
logging setup, and production deployment settings.
"""
import dotenv
import logging
from langchain.globals import set_debug, set_verbose
from src.core.api import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting HelpHub API server")

    # Load environment variables
    dotenv.load_dotenv()
    
    # Enable LangChain debugging
    set_debug(True)
    set_verbose(True)
    
    # TODO for participants:
    # - Add configuration from environment variables
    # - Include SSL/TLS configuration for production
    # - Add health checks and monitoring endpoints
    # - Configure CORS for production use
    # - Add rate limiting and authentication
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
    )
