"""Tests for the Python SQLite Release Readiness Auditor."""
import json
import sqlite3
import subprocess
import shutil
from pathlib import Path

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

def test_report_exists_and_valid():
    """Verify that the JSON report is generated and is a valid JSON."""
    assert REPORT_PATH.exists()
    try:
        with open(REPORT_PATH, 'r') as f:
            json.load(f)
    except json.JSONDecodeError:
        assert False, "Generated report.json is not valid JSON"

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
    assert blocker["policy_section"] == "1.1 API Breaking Changes", f"Expected exact heading '1.1 API Breaking Changes', got '{blocker['policy_section']}'"
    
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
    assert blocker["policy_section"] == "1.2 Flaky Tests", f"Expected exact heading '1.2 Flaky Tests', got '{blocker['policy_section']}'"

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
    assert blocker["policy_section"] == "1.3 Database Migrations", f"Expected exact heading '1.3 Database Migrations', got '{blocker['policy_section']}'"

    assert "description" in blocker
    assert len(blocker["description"]) > 10, "Description must be a meaningful sentence"

def test_non_blockers_excluded():
    """Verify that valid/passing items (e.g. non-breaking changes, excepted migrations) are excluded."""
    report = load_report()
    
    api_ids = [b["id"] for b in report["blockers"] if b["type"] == "API_CHANGE"]
    assert "api-001" not in api_ids, "api-001 (ARB-approved) should not be an API blocker"
    assert "api-003" not in api_ids, "api-003 (non-breaking) should not be an API blocker"
    assert "api-004" not in api_ids, "api-004 (0 traffic) should not be an API blocker"

    migration_ids = [b["id"] for b in report["blockers"] if b["type"] == "MIGRATION"]
    assert "TKT-100" not in migration_ids, "TKT-100 (has rollback plan) should not be a migration blocker"
    assert "TKT-102" not in migration_ids, "TKT-102 (has exception tag) should not be a migration blocker"
    assert "TKT-104" not in migration_ids, "TKT-104 (has APPROVED linked exception) should not be a migration blocker"
def test_overall_status_and_summary_counts():
    """Verify that the overall status reflects blockers and summary counts are accurate."""
    report = load_report()
    assert report["status"] == "BLOCKED"
    assert report["summary"]["total_blockers"] == 3
    assert report["summary"]["api_blockers"] == 1
    assert report["summary"]["test_blockers"] == 1
    assert report["summary"]["migration_blockers"] == 1

def test_dynamic_handbook_extraction():
    """Verify that the tool dynamically extracts policies from the handbook instead of hardcoding."""
    
    # We will modify the handbook to change the thresholds and verify the tool respects them.
    # The flaky test 'test_payment_gateway' has 4 failures in 7 days.
    # If we change the handbook to say "failed more than 5 times", it should NO LONGER be a blocker.
    
    handbook = Path("/app/environment/docs/handbook.md") if Path("/app/environment/docs/handbook.md").exists() else Path("/app/docs/handbook.md")
    original_text = handbook.read_text(encoding='utf-8')
    
    # Change "3 times" to "5 times"
    modified_text = original_text.replace("3 times", "5 times")
    handbook.write_text(modified_text, encoding='utf-8')
    
    try:
        # Re-run the tool
        subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)
        
        # Load the new report
        assert REPORT_PATH.exists()
        with open(REPORT_PATH, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # It should no longer flag test_payment_gateway
        test_blockers = [b for b in report["blockers"] if b["type"] == "FLAKY_TEST"]
        assert len(test_blockers) == 0, "The flaky test threshold was dynamically modified to 5, but the test with 4 failures was still flagged. The tool is hardcoding thresholds!"
        
    finally:
        # Restore the handbook
        handbook.write_text(original_text, encoding='utf-8')
        # Re-run the tool one last time to restore report.json back to the original fully blocked state for subsequent tests
        subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)

def test_time_handling_boundary(tmp_path):
    """Verify that the tool respects the specific boundary edge cases for time and flaky counts."""
    report = load_report()
    
    test_blockers = [b["id"] for b in report["blockers"] if b["type"] == "FLAKY_TEST"]
    assert "TEST-test_edge_case_fail_count" not in test_blockers, "A test with exactly 3 failures was flagged, but the policy says 'more than 3'."
    assert "TEST-test_edge_case_old_fail" not in test_blockers, "A test with old failures outside the 7-day window was incorrectly flagged."
    assert "TEST-test_edge_case_pass_time" not in test_blockers, "A test with a passing run within the 48-hour window was incorrectly flagged."

def test_time_handling_dynamic(tmp_path):
    """Verify that the tool strictly uses MAX(run_time) and NOT system datetime.now()."""
    
    # We will insert a completely new test run that occurred 5 years ago, and make it the NEW MAX(run_time).
    # Then we will insert a test that failed 4 times exactly 2 days before that 5-year-old date.
    # If the tool uses datetime.now(), this 5-year-old failure will be ignored because it's far outside the 7-day window.
    # If the tool correctly uses MAX(run_time), it will flag it as a blocker.
    
    dbs_to_modify = []
    if Path("/app/release_data.db").exists():
        dbs_to_modify.append("/app/release_data.db")
    if Path("/app/environment/release_data.db").exists():
        dbs_to_modify.append("/app/environment/release_data.db")

    backups = {}
    for db in dbs_to_modify:
        backup_path = str(tmp_path / f"time_backup_{len(backups)}.db")
        shutil.copy2(db, backup_path)
        backups[db] = backup_path
    
    try:
        for db in dbs_to_modify:
            conn = sqlite3.connect(db)
            c = conn.cursor()
            
            # The fixed_now in generate_data.py was 2024-01-01
            # Let's insert a NEW max time: 2010-01-01
            # Wait! The current max time is 2024-01-01. If we insert 2010-01-01, it won't be the MAX!
            # So we must insert a NEW MAX time: 2030-01-01!
            c.execute("INSERT INTO test_runs VALUES ('time-test-ref', 'test_final_reference_2', 'PASSED', '2030-01-01 12:00:00')")
            
            # Insert a flaky test that fails exactly 1 day before the new max (2029-12-31)
            # This is 3 years IN THE FUTURE. A tool using datetime.now() (2026) will think these tests haven't happened yet,
            # or if it does count them, we can test a date in the past instead!
            
            # To be absolutely sure, let's just DELETE all existing test runs, so the MAX is whatever we set.
            c.execute("DELETE FROM test_runs")
            
            # Set the new MAX to 2015-01-10
            c.execute("INSERT INTO test_runs VALUES ('time-test-ref', 'test_final_reference_2', 'PASSED', '2015-01-10 12:00:00')")
            
            # Insert 4 failures for 'test_payment_gateway' on 2015-01-05 (5 days before MAX)
            for i in range(4):
                c.execute(f"INSERT INTO test_runs VALUES ('time-fail-{i}', 'test_payment_gateway', 'FAILED', '2015-01-05 12:0{i}:00')")
            
            conn.commit()
            conn.close()

        # Re-run the tool
        subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)
        
        report = load_report()
        test_blockers = [b["id"] for b in report["blockers"] if b["type"] == "FLAKY_TEST"]
        
        assert "TEST-test_payment_gateway" in test_blockers, "The tool failed to flag a flaky test relative to the MAX(run_time). It is likely incorrectly using datetime.now() instead of the database's historical time!"
        
    finally:
        for db, backup_path in backups.items():
            shutil.copy2(backup_path, db)
        subprocess.run(["python3", str(CLI_PATH)], capture_output=True, timeout=30)
