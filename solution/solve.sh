#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "Running oracle solution..."
if [ -f "/oracle/auditor_script.py" ]; then
    echo "Found /oracle/auditor_script.py"
else
    echo "ERROR: /oracle/auditor_script.py NOT FOUND! Current contents of /oracle:"
    ls -la /oracle || true
    echo "Contents of /app/solution:"
    ls -la /app/solution || true
fi

echo "Checking environment files..."
ls -la /app/environment/docs/handbook.md || echo "handbook.md missing from /app/environment/docs/"
ls -la /app/docs/handbook.md || echo "handbook.md missing from /app/docs/"
ls -la /app/environment/release_data.db || echo "release_data.db missing from /app/environment/"
ls -la /app/release_data.db || echo "release_data.db missing from /app/"

python3 /oracle/auditor_script.py
