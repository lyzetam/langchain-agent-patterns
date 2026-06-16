# Build a servable LangGraph container for the lead-lifecycle workflow.
#
#   docker build -t lead-lifecycle-agent .
#   docker run --rm -p 8000:8000 --env-file .env lead-lifecycle-agent
#
# Serves the `lead_lifecycle` graph (see langgraph.json) over the LangGraph API.
FROM python:3.12-slim

WORKDIR /app

# Install deps first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e . "langgraph-cli[inmem]>=0.2"

# App code (skills/, workflow.py, agents, etc.)
COPY . .

EXPOSE 8000

# langgraph-cli reads langgraph.json and serves the graph.
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
