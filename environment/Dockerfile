FROM mcr.microsoft.com/devcontainers/python:3.12@sha256:d43f1b9f431b963d38ab32ed1e4b727aa6656e3c30e51b8f44dbeac5f7bbcbf7
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
        procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY docs/ /app/docs/
COPY src/ /app/src/
COPY config/ /app/config/
COPY pyproject.toml Makefile /app/
COPY release_data.db /app/release_data.db

ENV PYTHONPATH=/app
