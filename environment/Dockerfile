FROM python:3.12-slim@sha256:d17ec4bf0e2d1921356e2971a81bb1a09bb68d374d6c41b802deccbe13af58dd
WORKDIR /app

# Install required system tools (tmux, asciinema are mandatory for the agent)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
        procps \
    && rm -rf /var/lib/apt/lists/*

# Pre-download test dependencies to a cache so we can install them offline in test.sh
RUN mkdir -p /tmp/test-wheels && pip download -d /tmp/test-wheels pytest==8.4.1 pytest-json-ctrf==0.5.0 iniconfig packaging pluggy

# Copy task files (making sure not to copy tests/ or solution/)
COPY docs/ /app/docs/
COPY src/ /app/src/
COPY config/ /app/config/
COPY release_data.db /app/release_data.db

# Ensure Python can find the src modules
ENV PYTHONPATH=/app
