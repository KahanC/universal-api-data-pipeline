# Data Quality Report — synthetic_transactions

**Generated:** 2026-11-16T20:44:51.356048+00:00
**Status:** ALERT
**Alerts:** 4

## Dataset comparison

| Metric | Previous | Current |
|---|---:|---:|
| Records | 100 | 60 |
| Completeness (%) | 100.0 | 87.5 |

## Detected anomalies

| Severity | Check | Description |
|---|---|---|
| HIGH | ROW_COUNT_DROP | Record count decreased 40.00% |
| HIGH | COMPLETENESS_DROP | Completeness declined 12.50 percentage points |
| MEDIUM | DUPLICATE_INCREASE | Duplicate row count increased |
| HIGH | SCHEMA_DRIFT | Removed columns: ['Region']; Added columns: [] |
