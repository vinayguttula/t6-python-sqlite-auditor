# SQLite Release Readiness Auditor

A Python CLI tool is required to act as a Release Readiness Auditor.

The tool will be provided with a large Engineering Handbook located at `/app/docs/handbook.md` and a seeded SQLite database located at `/app/release_data.db`.

The tool must analyze both sources and produce a JSON report at `/app/report.json`.

**Requirements:**
1. The tool must dynamically extract the release readiness policies from the Engineering Handbook, specifically the thresholds and constraints for API Breaking Changes, Flaky Tests, and Database Migrations.
2. The tool must evaluate the data in the SQLite database (`tickets`, `test_runs`, `api_changes`) against the extracted policies to identify any violations that block the release.
   - API breaking change violations must be assigned a `HIGH` severity.
   - Flaky test violations must be assigned a `HIGH` severity. The ID for these violations must be constructed as `TEST-<test_name>`.
   - Database migration violations must be assigned a `CRITICAL` severity.
3. The tool must output its findings to `/app/report.json` with the exact schema below:

```json
{
  "status": "BLOCKED", 
  "blockers": [
    {
      "id": "<id_from_db_or_constructed>",
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
