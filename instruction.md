# SQLite Release Readiness Auditor

We need you to build a Python CLI that acts as a Release Readiness Auditor for our system.

You are provided with a large Engineering Handbook located at `/app/docs/handbook.md` and a seeded SQLite database located at `/app/release_data.db`.

Your task is to analyze both sources and produce a JSON report at `/app/report.json`.

**Requirements:**
1. Extract the release readiness policies from the Engineering Handbook (specifically the sections on API Breaking Changes, Flaky Tests, and Database Migrations).
2. Query the SQLite database (`tickets`, `test_runs`, `api_changes`) to identify any items that violate these policies and block the release.
3. Your Python script must read the DB and handbook, and generate `/app/report.json` with the exact schema below:

```json
{
  "status": "BLOCKED",
  "blockers": [
    {
      "id": "<id_from_db>",
      "type": "<API_CHANGE | FLAKY_TEST | MIGRATION>",
      "severity": "<HIGH | CRITICAL>",
      "description": "<A brief sentence describing the violation>",
      "policy_section": "<The section heading from the handbook that was violated>"
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

Please write your Python script and execute it to generate the report.
