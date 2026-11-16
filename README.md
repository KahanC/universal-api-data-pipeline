
# Universal API Data Pipeline

**A configurable Python ETL framework for REST API ingestion, automated data profiling, historical monitoring, and anomaly detection.**

Built to transform raw API responses into validated, analysis-ready datasets and automated reporting outputs.

**Tech Stack:** Python | REST APIs | Pandas | SQLite | OpenPyXL | GitHub Actions

## Key Features

- **Configurable API connectors:** Retrieve data from different REST APIs using JSON configuration files.
- **Automated pagination:** Collect multi-page API responses.
- **Authentication support:** Configurable API authentication methods.
- **JSON normalization:** Transform nested API responses into structured tabular datasets.
- **Data validation:** Detect missing values, duplicate records, and invalid numerical values.
- **Automatic data profiling:** Generate completeness metrics, column statistics, and categorical summaries.
- **Historical monitoring:** Persist dataset quality snapshots in SQLite.
- **Anomaly detection:** Identify record-count drops, completeness deterioration, duplicate increases, and schema drift.
- **Automated reporting:** Export data and monitoring results to CSV, Excel, JSON, and Markdown.
- **Continuous integration:** Automated Python unit testing using GitHub Actions.

## Architecture

```text
              REST API Sources
                     |
              JSON Configurations
                     |
               API Client
                     |
             Pagination Engine
                     |
             JSON Normalization
                     |
              Data Validation
                     |
             Statistical Profiling
                     |
             Historical Snapshots
                  (SQLite)
                     |
              Anomaly Detection
                     |
              Report Generation
                     |
       +-------------+-------------+
       |             |             |
     CSV/Excel    JSON/Markdown   SQLite
     Reports      Monitoring      History
```

## Supported API Examples

| API | Dataset | Purpose |
|---|---|---|
| World Bank API | GDP indicators | Economic time-series ingestion |
| JSONPlaceholder | User records | Nested JSON normalization |

The pipeline is designed to support additional compatible REST APIs through configuration.

## Automated Data Profiling

Each pipeline execution generates a statistical profile containing:

- Dataset dimensions and completeness
- Missing-value counts and percentages
- Duplicate-record counts
- Column-level data types
- Numerical summary statistics
- Categorical distributions

Profiling results are integrated into the Excel reporting workflow.

## Historical Monitoring & Anomaly Detection

The system stores historical dataset profiles in SQLite and compares subsequent runs against previous snapshots.

| Detection Rule | Description |
|---|---|
| Row Count Drop | Detects significant reductions in retrieved records |
| Completeness Drop | Detects deterioration in data completeness |
| Duplicate Increase | Detects increases in duplicate records |
| Schema Drift | Detects added or removed columns |

Monitoring results are exported in machine-readable JSON, human-readable Markdown, and Excel formats.

## Anomaly Detection Demonstration

A synthetic transaction dataset demonstrates four monitoring alerts:

| Metric | Previous Run | Current Run |
|---|---:|---:|
| Records | 100 | 60 |
| Completeness | 100% | 87.5% |
| Duplicate Rows | 0 | 1 |
| Columns | 3 | 2 |

**Detected anomalies:**
- 40% record-count reduction
- 12.5 percentage-point completeness deterioration
- Increased duplicate records
- Schema drift

### Example Monitoring Reports

- [JSON Monitoring Report](examples/reports/synthetic_transactions_monitoring.json)
- [Markdown Monitoring Report](examples/reports/synthetic_transactions_monitoring.md)
- [Excel Monitoring Report](examples/reports/synthetic_transactions_monitoring.xlsx)

All demonstration data is synthetic.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/KahanC/universal-api-data-pipeline.git
cd universal-api-data-pipeline
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the World Bank pipeline

```bash
python src/run_pipeline.py --config configs/world_bank.json
```

### 5. Run the JSONPlaceholder pipeline

```bash
python src/run_pipeline.py --config configs/users.json
```

Generated data and reports are saved in the `outputs/` directory.

## Run the Anomaly Demonstration

```bash
python examples/demo_anomalies.py
```

This generates synthetic anomaly monitoring reports under `examples/reports/`.

## Automated Testing

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

The project includes **23 automated tests** covering:

- API pagination
- Data validation
- Statistical profiling
- Historical snapshot storage
- Anomaly detection
- Monitoring report generation

GitHub Actions executes the test suite on pushes and pull requests to the main branch.

## Project Structure

```text
universal-api-data-pipeline/
├── .github/workflows/
│   └── python-ci.yml
├── configs/
│   ├── world_bank.json
│   └── users.json
├── examples/
│   ├── demo_anomalies.py
│   └── reports/
├── src/
│   ├── api_client.py
│   ├── pagination.py
│   ├── validation.py
│   ├── profiling.py
│   ├── history.py
│   ├── anomaly_detection.py
│   ├── monitoring_reports.py
│   ├── excel_report.py
│   └── run_pipeline.py
├── tests/
├── requirements.txt
└── README.md
```

## Security & Reproducibility

- Credentials are excluded from version control.
- Generated datasets and local SQLite databases are ignored by Git.
- Public API examples require no private credentials.
- Unit tests use controlled test data.
- Dependency versions are specified in `requirements.txt`.

## Engineering Focus

This project demonstrates reusable API integration, ETL architecture, automated data-quality controls, historical monitoring, anomaly detection, and reproducible reporting.

The framework extends an earlier Amazon Seller Central invoicing automation concept into a generic, multi-source data engineering system.
EOF
