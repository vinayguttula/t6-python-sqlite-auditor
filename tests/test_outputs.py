"""Tests for the Python SQLite Release Readiness Auditor."""
import json
import os
import pytest
from pathlib import Path
import subprocess

REPORT_PATH = Path("/app/report.json")
DB_PATH = Path("/app/environment/release_data.db") if Path("/app/environment/release_data.db").exists() else Path("/app/release_data.db")
CLI_PATH = Path("/app/src/cli.py")

def load_report():
    """Helper to load the report.json"""
    assert REPORT_PATH.exists(), "The report.json file was not generated."
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_tool_is_runnable():
    """Verify that a Python CLI tool exists and is runnable."""
    assert CLI_PATH.exists(), "The required /app/src/cli.py entry point does not exist."
    result = subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)
    assert result.returncode == 0, f"The CLI tool failed to execute cleanly. Error: {result.stderr.decode()}"
    assert REPORT_PATH.exists(), "The CLI tool did not generate the report.json file."

def test_report_schema():
    """Verify the output JSON has the correct required schema."""
    report = load_report()
    
    assert "status" in report
    assert "blockers" in report
    assert "summary" in report
    assert isinstance(report["blockers"], list)
    
    summary = report["summary"]
    assert "total_blockers" in summary
    assert "api_blockers" in summary
    assert "test_blockers" in summary
    assert "migration_blockers" in summary

def test_api_blocker_detection():
    """Verify that unapproved breaking API changes are correctly flagged."""
    report = load_report()
    
    api_blockers = [b for b in report["blockers"] if b["type"] == "API_CHANGE"]
    assert len(api_blockers) == 1, "Expected exactly 1 API blocker"
    
    blocker = api_blockers[0]
    assert blocker["id"] == "api-002"
    assert blocker["severity"] == "HIGH"
    assert "1.1 API Breaking Changes" in blocker["policy_section"]
    
    assert "description" in blocker
    assert len(blocker["description"]) > 10, "Description must be a meaningful sentence"

def test_flaky_test_detection():
    """Verify that stale flaky tests are flagged with the correct TEST-<name> ID."""
    report = load_report()
    
    test_blockers = [b for b in report["blockers"] if b["type"] == "FLAKY_TEST"]
    assert len(test_blockers) == 1, "Expected exactly 1 flaky test blocker"
    
    blocker = test_blockers[0]
    assert blocker["id"] == "TEST-test_payment_gateway"
    assert blocker["severity"] == "HIGH"
    assert "1.2 Flaky Tests" in blocker["policy_section"]

    assert "description" in blocker
    assert len(blocker["description"]) > 10, "Description must be a meaningful sentence"

def test_migration_blocker_detection():
    """Verify that migrations without rollback plans or exceptions are flagged."""
    report = load_report()
    
    migration_blockers = [b for b in report["blockers"] if b["type"] == "MIGRATION"]
    assert len(migration_blockers) == 1, "Expected exactly 1 migration blocker"
    
    blocker = migration_blockers[0]
    assert blocker["id"] == "TKT-101"
    assert blocker["severity"] == "CRITICAL"
    assert "1.3 Database Migrations" in blocker["policy_section"]

    assert "description" in blocker
    assert len(blocker["description"]) > 10, "Description must be a meaningful sentence"

def test_non_blockers_excluded():
    """Verify that valid/passing items (e.g. non-breaking changes, excepted migrations) are excluded."""
    report = load_report()
    
    api_ids = [b["id"] for b in report["blockers"] if b["type"] == "API_CHANGE"]
    assert "api-001" not in api_ids, "api-001 (ARB-approved) should not be an API blocker"
    assert "api-003" not in api_ids, "api-003 (non-breaking) should not be an API blocker"

    migration_ids = [b["id"] for b in report["blockers"] if b["type"] == "MIGRATION"]
    assert "TKT-100" not in migration_ids, "TKT-100 (has rollback plan) should not be a migration blocker"
    assert "TKT-102" not in migration_ids, "TKT-102 (has exception tag) should not be a migration blocker"

def test_overall_status_and_summary_counts():
    """Verify that the overall status reflects blockers and summary counts are accurate."""
    report = load_report()
    assert report["status"] == "BLOCKED"
    assert report["summary"]["total_blockers"] == 3
    assert report["summary"]["api_blockers"] == 1
    assert report["summary"]["test_blockers"] == 1
    assert report["summary"]["migration_blockers"] == 1

def test_dynamic_extraction():
    """Verify that the tool dynamically extracts policies instead of hardcoding answers."""
    import sqlite3
    
    # Modify all possible databases to make sure the CLI picks up the modification
    dbs_to_modify = ["/app/environment/release_data.db", "/app/release_data.db"]
    for db in dbs_to_modify:
        if os.path.exists(db):
            conn = sqlite3.connect(db)
            c = conn.cursor()
            c.execute("DELETE FROM api_changes WHERE id = 'api-002'")
            c.execute("DELETE FROM test_runs WHERE test_name = 'test_payment_gateway'")
            c.execute("DELETE FROM tickets WHERE id = 'TKT-101'")
            conn.commit()
            conn.close()

    # Re-run the tool
    subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)
    
    # Load the new report
    assert REPORT_PATH.exists()
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    assert report["status"] == "READY"
    assert report["summary"]["total_blockers"] == 0
    assert len(report["blockers"]) == 0
