"""Configuration settings for the auditor."""
import os

DB_PATH = os.getenv("DB_PATH", "/app/release_data.db")
HANDBOOK_PATH = os.getenv("HANDBOOK_PATH", "/app/docs/handbook.md")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/app/report.json")
