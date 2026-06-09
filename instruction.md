# SQLite Release Readiness Auditor

A Python CLI tool is required to act as a Release Readiness Auditor.

The tool will be provided with a large Engineering Handbook located at `/app/docs/handbook.md` and a seeded SQLite database located at `/app/release_data.db`. It will also have access to configuration files located in `/app/config/`.

The tool must analyze these sources and produce a JSON report at `/app/report.json`.

**Requirements:**
1. The tool must dynamically extract the release readiness policies from the Engineering Handbook, specifically the thresholds and constraints for API Breaking Changes, Flaky Tests, and Database Migrations.
2. The tool must evaluate the data in the SQLite database (`tickets`, `test_runs`, `api_changes`, `exceptions`) against the extracted policies and the auxiliary configuration files to identify any violations that block the release.
   - API breaking change violations must be assigned a `HIGH` severity. They are ONLY considered blockers if the endpoint has received traffic in the last 24 hours (cross-reference with `/app/config/metrics.csv`).
   - Flaky test violations must be assigned a `HIGH` severity. The ID for these violations must be constructed as `TEST-<test_name>`. They are ONLY considered blockers if they belong to a Tier-1 service (cross-reference `test_name` with `/app/config/test_mapping.json` to find the service, then check the tier in `/app/config/ownership.json`).
   - Database migration violations must be assigned a `CRITICAL` severity. They are allowed to proceed without a rollback plan if they have a linked ticket whose status in the `exceptions` table is `APPROVED`.
3. **IMPORTANT - Time Handling:** Because the database contains historical records, your script MUST assume the "current time" is exactly the timestamp of the most recent test run in the `test_runs` table (`MAX(run_time)`). Do NOT use the system's actual `datetime.now()`.
4. Your main CLI tool MUST be located at `/app/src/cli.py`. The testing framework will execute this file directly.
5. The tool must output its findings to `/app/report.json`. The report must indicate whether the release is blocked and list any violations with their type, severity, description, ID, and policy section (which must be the exact, full section heading from the handbook that was violated, including its numeric prefix). It must also provide a summary of the total blocker counts broken down by category.

**Example Expected Output:**
```json
{
  "status": "BLOCKED", 
  "blockers": [
    {
      "id": "api-002",
      "type": "API_CHANGE",
      "severity": "HIGH",
      "description": "Breaking API change to /v1/payments approved by 'Engineering Manager' instead of Architecture Review Board (ARB).",
      "policy_section": "1.1 API Breaking Changes"
    },
    {
      "id": "TEST-test_payment_gateway",
      "type": "FLAKY_TEST",
      "severity": "HIGH",
      "description": "Test test_payment_gateway has 4 failures in last 7 days and 0 passes in last 48 hours.",
      "policy_section": "1.2 Flaky Tests"
    },
    {
      "id": "TKT-101",
      "type": "MIGRATION",
      "severity": "CRITICAL",
      "description": "Migration ticket TKT-101 missing rollback plan and lacks exception tag.",
      "policy_section": "1.3 Database Migrations"
    }
  ],
  "summary": {
    "total_blockers": 3,
    "api_blockers": 1,
    "test_blockers": 1,
    "migration_blockers": 1
  }
}
```
*Note: If there are no blockers, `status` should be "READY", the `blockers` array should be empty, and the counts in `summary` should all be 0.*
