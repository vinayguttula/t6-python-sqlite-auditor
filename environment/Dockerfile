FROM mcr.microsoft.com/devcontainers/python:3.12@sha256:d43f1b9f431b963d38ab32ed1e4b727aa6656e3c30e51b8f44dbeac5f7bbcbf7
WORKDIR /app

# Install required system tools (tmux, asciinema are mandatory for the agent)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
        procps \
    && rm -rf /var/lib/apt/lists/*

# Install solution dependencies (PyYAML) AND test dependencies directly in the image
RUN pip install --no-cache-dir pyyaml==6.0.3 pytest==8.4.1 pytest-json-ctrf==0.5.0 iniconfig packaging pluggy

# Copy task files (making sure not to copy tests/ or solution/)
COPY docs/ /app/docs/
COPY src/ /app/src/
COPY config/ /app/config/
COPY pyproject.toml Makefile /app/
COPY release_data.db /app/release_data.db

# Ensure Python can find the src modules
ENV PYTHONPATH=/app
