# Architecture Overview

The SQLite Release Readiness Auditor is designed as a standalone Python CLI.

## Core Components
- **CLI Interface:** Handles command-line arguments and configuration loading (via `src/cli.py`).
- **Policy Engine:** Responsible for parsing the unstructured `handbook.md` to dynamically extract current business rules.
- **Database Layer:** Interfaces with the release readiness SQLite database to query tickets, test runs, and API changes.
- **Reporting Module:** Aggregates findings and outputs the final `report.json` payload.

## Data Flow
1. The tool initializes and loads configuration variables (e.g., paths to the handbook and DB).
2. The Policy Engine runs regex extraction on the markdown handbook to determine dynamic thresholds.
3. The DB Layer establishes a read-only connection to SQLite.
4. Queries are executed to identify blockers based on the thresholds.
5. The JSON report is flushed to disk.
