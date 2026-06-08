"""Configuration settings for the auditor CLI."""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Input sources
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "release_data.db"))
HANDBOOK_PATH = os.getenv("HANDBOOK_PATH", str(BASE_DIR / "docs" / "handbook.md"))

# Output destination
OUTPUT_PATH = os.getenv("OUTPUT_PATH", str(BASE_DIR / "report.json"))

# Audit Settings
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"
