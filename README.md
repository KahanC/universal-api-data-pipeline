
# Universal API Data Pipeline

[![Python CI](https://github.com/KahanC/universal-api-data-pipeline/actions/workflows/python-ci.yml/badge.svg)](https://github.com/KahanC/universal-api-data-pipeline/actions/workflows/python-ci.yml)

**A configurable Python ETL framework for REST API ingestion, automated data profiling, historical monitoring, and anomaly detection.**

Built to transform raw API responses into validated, analysis-ready datasets and automated reporting outputs.

**Tech Stack:** Python | REST APIs | Pandas | SQLite | OpenPyXL | GitHub Actions

**A configuration-driven Python ETL framework for ingesting REST API data, validating data quality, profiling datasets, detecting anomalies, and monitoring changes across pipeline runs.**

Built to demonstrate production-oriented data engineering practices, including reusable API connectors, pagination, automated quality checks, historical monitoring, and reproducible reporting.

### Key capabilities

| Capability | Implementation |
|---|---|
| API ingestion | Reusable REST API client with configurable endpoints and authentication |
| ETL processing | JSON normalization and configuration-driven transformations |
| Data quality | Missing-value, uniqueness, and non-negative validation |
| Automatic profiling | Completeness, duplicates, numeric statistics, and categorical distributions |
| Historical monitoring | SQLite snapshots and comparisons between pipeline runs |
| Anomaly detection | Schema drift, row-count changes, completeness drops, and duplicate increases |
| Reporting | Excel, CSV, JSON, and Markdown outputs |
| Automated testing | Python `unittest` suite with GitHub Actions CI |

### Architecture

```text
REST APIs
   |
   v
Configurable API Client
   |
   v
Pagination & JSON Extraction
   |
   v
Data Transformation
   |
   v
Data Quality Validation
   |
   v
Automatic Data Profiling
   |
   +------> Historical SQLite Snapshots
   |                  |
   |                  v
   |           Anomaly Detection
   |                  |
   v                  v
CSV / Excel       Monitoring Reports
                  JSON / Markdown / Excel
```

### Example integrations

- **World Bank API:** Historical GDP data retrieved and transformed into structured economic datasets.
- **JSONPlaceholder API:** Nested user records normalized into tabular data.
- **Synthetic transaction monitoring:** Demonstrates anomaly detection using controlled example data.

### Example monitoring outputs

- [JSON monitoring report](examples/reports/synthetic_transactions_monitoring.json)
- [Markdown monitoring report](examples/reports/synthetic_transactions_monitoring.md)
- [Excel monitoring report](examples/reports/synthetic_transactions_monitoring.xlsx)
- [Synthetic anomaly demonstration](examples/demo_anomalies.py)

### Engineering decisions

**Configuration over hardcoding:** API-specific settings are separated from pipeline logic, allowing different data sources to reuse the same processing framework.

**Validation before reporting:** Data quality checks run before downstream reporting to prevent invalid datasets from silently propagating.

**Historical monitoring:** SQLite stores lightweight pipeline snapshots, enabling comparisons between runs without requiring an external database server.

**Testable architecture:** Pagination, validation, profiling, historical storage, and anomaly detection are covered by automated unit tests.

**Portable execution:** The framework runs locally using Python and is tested through GitHub Actions without requiring Docker or cloud infrastructure.
