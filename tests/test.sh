#!/usr/bin/env bash
set -uo pipefail

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
    mkdir -p /logs/verifier
    echo 0 > /logs/verifier/reward.txt
    return 0 2>/dev/null || true
fi

# Install test dependencies from the pre-downloaded cache (offline)
pip install --no-index --find-links=/tmp/test-wheels pytest==8.4.1 pytest-json-ctrf==0.5.0 iniconfig packaging pluggy >/dev/null 2>&1

mkdir -p /logs/verifier

# The platform mounts tests into /tests/
python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
rc=$?

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
