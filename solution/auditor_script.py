import sqlite3
import json
import re
from datetime import datetime, timedelta

def run_audit():
    db_path = '/app/release_data.db'
    handbook_path = '/app/docs/handbook.md'
    output_path = '/app/report.json'

    report = {
        "status": "READY",
        "blockers": [],
        "summary": {
            "total_blockers": 0,
            "api_blockers": 0,
            "test_blockers": 0,
            "migration_blockers": 0
        }
    }

    try:
        with open(handbook_path, 'r', encoding='utf-8') as f:
            handbook_content = f.read()
    except FileNotFoundError:
        print(f"Error: {handbook_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return

    # Extract Policy 1: API Changes Approver
    # Looks for: "...approved by the **Architecture Review Board (ARB)**..."
    api_policy_match = re.search(r'approved by the \*\*(.+?)\*\*', handbook_content)
    api_approver = api_policy_match.group(1) if api_policy_match else "Architecture Review Board (ARB)"

    # Extract Policy 2: Flaky Tests Thresholds
    # Looks for: "...failed more than 3 times in the last 7 days AND has not been fixed... within the last 48 hours."
    fail_thresh_match = re.search(r'failed more than (\d+) times in the last (\d+) days', handbook_content)
    fail_count_limit = int(fail_thresh_match.group(1)) if fail_thresh_match else 3
    days_limit = int(fail_thresh_match.group(2)) if fail_thresh_match else 7

    pass_thresh_match = re.search(r'within the last (\d+) hours', handbook_content)
    hours_limit = int(pass_thresh_match.group(1)) if pass_thresh_match else 48

    # Extract Policy 3: Migration Exception Tag
    # Looks for: "...exception label `[NO_ROLLBACK_REQUIRED]`..."
    migration_tag_match = re.search(r'exception label `(.+?)`', handbook_content)
    migration_tag = migration_tag_match.group(1) if migration_tag_match else "[NO_ROLLBACK_REQUIRED]"

    # Apply Policy 1
    c.execute("SELECT id, endpoint, approved_by FROM api_changes WHERE is_breaking = 1")
    for row in c.fetchall():
        api_id, endpoint, approved_by = row
        if api_approver not in approved_by:
            report["blockers"].append({
                "id": api_id,
                "type": "API_CHANGE",
                "severity": "HIGH",
                "description": f"Breaking API change to {endpoint} approved by '{approved_by}' instead of {api_approver}.",
                "policy_section": "1.1 API Breaking Changes"
            })
            report["summary"]["api_blockers"] += 1

    # Apply Policy 2
    c.execute("SELECT test_name FROM test_runs GROUP BY test_name")
    tests = c.fetchall()
    
    now = datetime.now()
    days_ago_str = (now - timedelta(days=days_limit)).isoformat(sep=' ')
    hours_ago_str = (now - timedelta(hours=hours_limit)).isoformat(sep=' ')

    for (test_name,) in tests:
        c.execute("SELECT COUNT(*) FROM test_runs WHERE test_name = ? AND status = 'FAILED' AND run_time >= ?", (test_name, days_ago_str))
        fail_count = c.fetchone()[0]
        
        if fail_count > fail_count_limit:
            c.execute("SELECT COUNT(*) FROM test_runs WHERE test_name = ? AND status = 'PASSED' AND run_time >= ?", (test_name, hours_ago_str))
            recent_pass_count = c.fetchone()[0]
            
            if recent_pass_count == 0:
                report["blockers"].append({
                    "id": f"TEST-{test_name}",
                    "type": "FLAKY_TEST",
                    "severity": "HIGH",
                    "description": f"Test {test_name} has {fail_count} failures in last {days_limit} days and 0 passes in last {hours_limit} hours.",
                    "policy_section": "1.2 Flaky Tests"
                })
                report["summary"]["test_blockers"] += 1

    # Apply Policy 3
    c.execute("SELECT id, summary, rollback_plan FROM tickets WHERE type = 'Migration'")
    for row in c.fetchall():
        tkt_id, summary, rollback_plan = row
        if not rollback_plan.strip() and migration_tag not in summary:
            report["blockers"].append({
                "id": tkt_id,
                "type": "MIGRATION",
                "severity": "CRITICAL",
                "description": f"Migration ticket {tkt_id} missing rollback plan and lacks exception tag.",
                "policy_section": "1.3 Database Migrations"
            })
            report["summary"]["migration_blockers"] += 1

    conn.close()

    report["summary"]["total_blockers"] = len(report["blockers"])
    if report["summary"]["total_blockers"] > 0:
        report["status"] = "BLOCKED"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
if __name__ == '__main__':
    run_audit()
