FROM ghcr.io/open-webui/open-webui:v0.6.18

# Set environment variables for OpenWebUI configuration
ENV OPENAI_API_BASE_URL=http://backend:8000/v1
ENV OPENROUTER_API_KEY=dummy-key-not-used
ENV WEBUI_NAME="Agentic Workflow Workbench"
ENV ENABLE_TAGS_GENERATION=false
ENV ENABLE_TITLE_GENERATION=false  
ENV ENABLE_FOLLOW_UP_GENERATION=false
ENV ENABLE_MODEL_WHITELISTING=false
ENV DEFAULT_MODELS=support-desk

# Expose the default OpenWebUI port
EXPOSE 8080