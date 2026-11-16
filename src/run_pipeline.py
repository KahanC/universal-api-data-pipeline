import argparse
import json
from pathlib import Path

import pandas as pd

from api_client import APIClient
from pagination import fetch_all_pages
from validation import validate_dataframe
from excel_report import export_excel_report
from profiling import profile_dataframe
from history import save_snapshot, get_latest_snapshots
from anomaly_detection import detect_anomalies
from monitoring_reports import build_report
import logging


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def run_pipeline(config_path):
    config_path = Path(config_path)

    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)

    logging.info("Running pipeline: %s", config["name"])

    client = APIClient(
        base_url=config["base_url"],
        auth_type=config.get("auth_type", "none"),
        token_env=config.get("token_env"),
    )

    records = fetch_all_pages(client, config)

    if not isinstance(records, list):
        raise ValueError(
            "Configured API response must resolve to a list"
        )

    df = pd.json_normalize(records)

    fields = config["fields"]

    missing = [
        field for field in fields if field not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing expected API fields: {missing}"
        )

    df = df[list(fields)].rename(columns=fields)

    if df.empty:
        raise ValueError("API returned no records")

    result = validate_dataframe(
        df, config.get("validation", {})
    )
    logging.info(
        "Validation passed: %s rows", result["rows"]
    )

    profile = profile_dataframe(df)

    logging.info(
        "Profiling complete: %.2f%% completeness, %s duplicates",
        profile["overview"]["completeness_pct"],
        profile["overview"]["duplicate_rows"],
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    name = config["name"]
    csv_path = OUTPUT_DIR / f"{name}.csv"
    excel_path = OUTPUT_DIR / f"{name}.xlsx"

    profile_dir = OUTPUT_DIR / f"{name}_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    for section in ("columns", "numeric", "categories"):
        profile[section].to_csv(
            profile_dir / f"{section}.csv",
            index=False,
        )


    (profile_dir / "overview.json").write_text(
        json.dumps(profile["overview"], indent=2),
        encoding="utf-8",
    )

    df.to_csv(csv_path, index=False)
    export_excel_report(
        df, excel_path, config, result, profile
    )

    print(f"Records processed: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"CSV exported: {csv_path}")
    print(f"Excel exported: {excel_path}")

    monitoring = config.get("monitoring", {})
    previous = get_latest_snapshots(
        config["name"], limit=1
    )

    if monitoring.get("enabled", True) and previous:
        report = detect_anomalies(
            {
                "overview": profile["overview"],
                "columns": profile["columns"].to_dict(
                    orient="records"
                ),
            },
            previous[0]["profile"],
            monitoring.get("thresholds"),
        )
    else:
        report = {
            "status": "baseline",
            "alert_count": 0,
            "alerts": [],
        }

    report_files = build_report(
        config["name"],
        report,
        OUTPUT_DIR,
    )

    logging.info(
        "Monitoring status: %s | Alerts: %s",
        report["status"],
        report["alert_count"],
    )

    logging.info(
        "Monitoring reports generated: %s",
        report_files["markdown"],
    )

    snapshot_id = save_snapshot(
        config["name"], profile
    )

    logging.info(
        "Historical snapshot saved: ID %s",
        snapshot_id
    )

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Run a configurable API data pipeline"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the API configuration JSON",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    args = parser.parse_args()

    run_pipeline(args.config)


if __name__ == "__main__":
    main()
