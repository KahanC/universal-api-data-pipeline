import json
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from monitoring_reports import build_report


class TestMonitoringReports(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp.name)

        self.report = {
            "status": "alert",
            "alert_count": 1,
            "summary": {
                "previous_rows": 100,
                "current_rows": 60,
                "previous_completeness": 100.0,
                "current_completeness": 87.5,
            },
            "alerts": [{
                "code": "ROW_COUNT_DROP",
                "severity": "high",
                "message": "Record count decreased 40%",
                "previous": 100,
                "current": 60,
            }],
        }

        self.paths = build_report(
            "test_pipeline",
            self.report,
            self.output_dir,
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_all_report_formats_created(self):
        for path in self.paths.values():
            self.assertTrue(path.exists())

    def test_json_report(self):
        data = json.loads(
            self.paths["json"].read_text()
        )

        self.assertEqual(data["pipeline"], "test_pipeline")
        self.assertEqual(data["status"], "alert")
        self.assertEqual(data["alert_count"], 1)
        self.assertEqual(
            data["alerts"][0]["code"],
            "ROW_COUNT_DROP",
        )

    def test_excel_report(self):
        wb = load_workbook(self.paths["excel"])

        self.assertEqual(
            wb.sheetnames,
            ["Overview", "Alerts"],
        )

        self.assertEqual(
            wb["Overview"]["B4"].value, 1
        )

        self.assertEqual(
            wb["Alerts"]["B2"].value,
            "ROW_COUNT_DROP",
        )


if __name__ == "__main__":
    unittest.main()
