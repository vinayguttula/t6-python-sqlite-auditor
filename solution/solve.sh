#!/usr/bin/env bash
set -euo pipefail

# Make sure we're using absolute paths
cd /app

python3 /oracle/auditor_script.py
