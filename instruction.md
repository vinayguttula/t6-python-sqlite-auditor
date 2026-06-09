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
3. **IMPORTANT - Time Handling:** Because the database contains historical records, your script MUST assume the "current time" is exactly the timestamp of the most recent test run in the `test_runs` table (`MAX(run_time)`). Do NOT use the system's actual `datetime.now()`.
4. Your main CLI tool MUST be located at `/app/src/cli.py`. The testing framework will execute this file directly.
5. The tool must output its findings to `/app/report.json`. The report must indicate whether the release is blocked (`BLOCKED` vs `READY`), list any violations with their type, severity, description, ID, and policy section (which must be the exact, full section heading from the handbook that was violated, including its numeric prefix), and provide a summary of the total blocker counts broken down by category.
