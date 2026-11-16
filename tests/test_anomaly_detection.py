import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from anomaly_detection import detect_anomalies


def make_profile(rows, completeness, duplicates, columns):
    return {
        "overview": {
            "rows": rows,
            "completeness_pct": completeness,
            "duplicate_rows": duplicates,
        },
        "columns": [{"column": c} for c in columns],
    }


class TestAnomalyDetection(unittest.TestCase):

    def setUp(self):
        self.previous = make_profile(
            100, 100, 0, ["ID", "Amount", "Region"]
        )

    def test_healthy_dataset(self):
        current = make_profile(
            100, 100, 0, ["ID", "Amount", "Region"]
        )

        result = detect_anomalies(
            current, self.previous
        )

        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["alert_count"], 0)

    def test_row_count_drop(self):
        current = make_profile(
            60, 100, 0, ["ID", "Amount", "Region"]
        )

        result = detect_anomalies(
            current, self.previous
        )

        self.assertIn(
            "ROW_COUNT_DROP",
            [a["code"] for a in result["alerts"]],
        )

    def test_completeness_drop(self):
        current = make_profile(
            100, 90, 0, ["ID", "Amount", "Region"]
        )

        result = detect_anomalies(
            current, self.previous
        )

        self.assertIn(
            "COMPLETENESS_DROP",
            [a["code"] for a in result["alerts"]],
        )

    def test_duplicate_increase(self):
        current = make_profile(
            100, 100, 5, ["ID", "Amount", "Region"]
        )

        result = detect_anomalies(
            current, self.previous
        )

        self.assertIn(
            "DUPLICATE_INCREASE",
            [a["code"] for a in result["alerts"]],
        )

    def test_schema_drift(self):
        current = make_profile(
            100, 100, 0, ["ID", "Amount"]
        )

        result = detect_anomalies(
            current, self.previous
        )

        self.assertIn(
            "SCHEMA_DRIFT",
            [a["code"] for a in result["alerts"]],
        )


if __name__ == "__main__":
    unittest.main()
