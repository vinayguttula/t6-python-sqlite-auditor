# Database Schema

## tickets
- `id` (TEXT): Ticket ID
- `type` (TEXT): Type of ticket (e.g., Migration, Feature)
- `summary` (TEXT): Ticket summary
- `rollback_plan` (TEXT): Rollback plan description
- `status` (TEXT): Current ticket status

## test_runs
- `id` (TEXT): Run ID
- `test_name` (TEXT): Name of the test
- `status` (TEXT): PASSED or FAILED
- `run_time` (TIMESTAMP): Time of the run

## api_changes
- `id` (TEXT): Change ID
- `endpoint` (TEXT): API endpoint
- `is_breaking` (BOOLEAN): 1 if breaking, 0 otherwise
- `approved_by` (TEXT): Name of approver
