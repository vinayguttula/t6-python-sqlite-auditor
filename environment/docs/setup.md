# Local Setup Guide

Follow these instructions to run the Auditor CLI locally:

## Prerequisites
- Python >= 3.12
- SQLite3 CLI (optional, for inspecting the DB)

## Installation
1. Clone the repository.
2. Install dependencies (currently none outside the standard library are strictly required, but a virtual environment is recommended).

## Running the Tool
Execute the CLI directly:
```bash
python3 src/cli.py
```

## Configuration
The tool relies on environment variables for overrides. See `src/config.py` for default values.
