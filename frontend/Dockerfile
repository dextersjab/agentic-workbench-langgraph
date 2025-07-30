FROM ghcr.io/open-webui/open-webui:v0.6.18

# Copy injection script and make it executable
USER root
COPY inject-monitor.sh /inject-monitor.sh
RUN chmod +x /inject-monitor.sh

# Set environment variables for OpenWebUI configuration
ENV OPENAI_API_BASE_URL=http://backend:8000/v1
ENV OPENAI_API_KEY=dummy-key-not-used
ENV WEBUI_NAME="Agentic Workflow Workbench"
ENV ENABLE_TAGS_GENERATION=false
ENV ENABLE_TITLE_GENERATION=false  
ENV ENABLE_FOLLOW_UP_GENERATION=false
ENV ENABLE_MODEL_WHITELISTING=false
ENV DEFAULT_MODELS=support-desk

# Stay as root for the injection, then switch in the script
# Use our injection script as entrypoint
ENTRYPOINT ["/inject-monitor.sh"]
CMD ["bash", "/app/backend/start.sh"]

# Expose the default OpenWebUI port
EXPOSE 8080