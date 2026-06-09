# SQLite Release Readiness Auditor

A Python CLI tool is required to act as a Release Readiness Auditor.

The tool will be provided with a large Engineering Handbook located at `/app/docs/handbook.md` and a seeded SQLite database located at `/app/release_data.db`. It will also have access to configuration files located in `/app/config/`. For the database schema, please refer to `/app/docs/schemas.md`.

**Functional Requirements:**

1. **Policy Extraction**: The tool must dynamically read and parse release readiness policies from the Engineering Handbook, specifically locating thresholds and constraints for API Breaking Changes, Flaky Tests, and Database Migrations. The numeric threshold values (e.g., the number *N* in "failed more than *N* times" or "within the last *N* hours") must be derived dynamically from the handbook text at runtime.
2. **Violation Evaluation**: The tool must cross-reference data in the SQLite database (`tickets`, `test_runs`, `api_changes`, `exceptions`) against the extracted policies and auxiliary configuration files to determine if any violations block the release.
   - **API Breaking Changes**: These violations must be assigned a `HIGH` severity. An API change is considered a blocker only if the endpoint received traffic in the last 24 hours (determined via `/app/config/metrics.csv`).
   - **Flaky Tests**: These violations must be assigned a `HIGH` severity. The ID for these violations must be constructed as `TEST-<test_name>`. A flaky test is considered a blocker only if it belongs to a Tier-1 service (determined by mapping the test name via `/app/config/test_mapping.json` to find the service, and looking up its tier in `/app/config/ownership.json`).
   - **Database Migrations**: These violations must be assigned a `CRITICAL` severity. Migrations are allowed to proceed without a rollback plan if they have a linked ticket whose status in the `exceptions` table is `APPROVED`.
3. **Time Handling**: Because the database contains historical records, the logical "current time" for all calculations must be exactly the timestamp of the most recent test run in the `test_runs` table (`MAX(run_time)`). The system's actual clock time should not be used.

**Execution and Setup Requirements:**

1. The main CLI entrypoint must be located at `/app/src/cli.py`. The testing framework will execute this file directly.
2. The tool must output its findings as a JSON file located at `/app/report.json`.
3. The report must indicate the overall status and list any violations with their type, severity, description, ID, and policy section (which must be the exact, full section heading from the handbook that was violated, including its numeric prefix). It must also provide a summary of the total blocker counts broken down by category.

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
