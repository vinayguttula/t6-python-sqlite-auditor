#!/usr/bin/env bash
set -uo pipefail

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
    mkdir -p /logs/verifier
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

mkdir -p /logs/verifier

# Install test dependencies here so they are not baked into the Docker image unnecessarily.
pip install pytest==8.4.1 pytest-json-ctrf==0.5.0 iniconfig==2.0.0 packaging==24.0 pluggy==1.5.0

# The platform mounts tests into /tests/
python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
rc=$?

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
