"""
Main entry point for the agentic workflows API.
"""

import dotenv
import logging
from langchain_core.globals import set_debug, set_verbose

# Import logging configuration (sets up file and console logging)

# App is imported as string for reload functionality below

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.info("Starting Agentic Workflow Workbench API server")

    # Load environment variables
    dotenv.load_dotenv()

    # Enable LangChain debugging
    set_debug(True)
    set_verbose(True)

    # TODO add configuration from environment variables?

    import uvicorn

    uvicorn.run(
        "src.core.api:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )
