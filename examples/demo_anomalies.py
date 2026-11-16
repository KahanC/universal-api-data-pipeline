import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profiling import profile_dataframe
from anomaly_detection import detect_anomalies
from monitoring_reports import build_report


def prepare(df):
    profile = profile_dataframe(df)
    return {
        "overview": profile["overview"],
        "columns": profile["columns"].to_dict(orient="records"),
    }


# Previous run: 100 clean transactions
previous = pd.DataFrame({
    "Order ID": range(1, 101),
    "Amount": [100.0] * 100,
    "Region": ["Canada"] * 100,
})

# Current run: 60 transactions with quality issues
current = pd.DataFrame({
    "Order ID": [1, 1] + list(range(3, 61)),
    "Amount": [None] * 15 + [100.0] * 45,
})

report = detect_anomalies(
    prepare(current),
    prepare(previous),
)

assert report["alert_count"] == 4, report

paths = build_report(
    "synthetic_transactions",
    report,
    ROOT / "examples" / "reports",
)

print("\nANOMALY DETECTION DEMONSTRATION")
print("=" * 45)
print("Status:", report["status"].upper())
print("Alerts detected:", report["alert_count"])

for alert in report["alerts"]:
    print(
        f"[{alert['severity'].upper()}] "
        f"{alert['code']}: {alert['message']}"
    )

print("\nGenerated reports:")
for path in paths.values():
    print(path)
