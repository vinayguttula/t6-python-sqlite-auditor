"""Tests for the Python SQLite Release Readiness Auditor."""
import json
import sqlite3
import pytest
from pathlib import Path

REPORT_PATH = Path("/app/report.json")
DB_PATH = Path("/app/release_data.db")

def load_report():
    """Helper to load the report.json"""
    assert REPORT_PATH.exists(), "The report.json file was not generated."
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_report_exists():
    """Verify that the JSON report is generated and is a valid JSON."""
    assert REPORT_PATH.exists()
    try:
        with open(REPORT_PATH, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        pytest.fail("Generated report.json is not valid JSON")

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
    
    # We seeded api-002 as a blocker (breaking, approved by Engineering Manager)
    api_blockers = [b for b in report["blockers"] if b["type"] == "API_CHANGE"]
    assert len(api_blockers) == 1, "Expected exactly 1 API blocker"
    
    blocker = api_blockers[0]
    assert blocker["id"] == "api-002"
    assert blocker["severity"] == "HIGH"
    assert "1.1 API Breaking Changes" in blocker["policy_section"]

def test_flaky_test_detection():
    """Verify that stale flaky tests (failing >3 times in 7d, no pass in 48h) are flagged."""
    report = load_report()
    
    # We seeded test_payment_gateway as a blocker
    test_blockers = [b for b in report["blockers"] if b["type"] == "FLAKY_TEST"]
    assert len(test_blockers) == 1, "Expected exactly 1 flaky test blocker"
    
    blocker = test_blockers[0]
    assert blocker["id"] == "TEST-test_payment_gateway"
    assert blocker["severity"] == "HIGH"
    assert "1.2 Flaky Tests" in blocker["policy_section"]

def test_migration_blocker_detection():
    """Verify that migrations without rollback plans or exceptions are flagged."""
    report = load_report()
    
    # We seeded TKT-101 as a blocker (no rollback, no exception)
    migration_blockers = [b for b in report["blockers"] if b["type"] == "MIGRATION"]
    assert len(migration_blockers) == 1, "Expected exactly 1 migration blocker"
    
    blocker = migration_blockers[0]
    assert blocker["id"] == "TKT-101"
    assert blocker["severity"] == "CRITICAL"
    assert "1.3 Database Migrations" in blocker["policy_section"]

def test_overall_status():
    """Verify that the overall status reflects the presence of blockers."""
    report = load_report()
    assert report["status"] == "BLOCKED"
    assert report["summary"]["total_blockers"] == 3
