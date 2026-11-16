import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from history import save_snapshot, get_latest_snapshots
from profiling import profile_dataframe


class TestHistory(unittest.TestCase):

    def test_save_and_retrieve_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "history.db"

            df = pd.DataFrame({
                "ID": [1, 2, 3],
                "Amount": [100, 200, 300],
            })

            profile = profile_dataframe(df)

            snapshot_id = save_snapshot(
                "test_api", profile, db_path
            )

            snapshots = get_latest_snapshots(
                "test_api", db_path=db_path
            )

            self.assertEqual(snapshot_id, 1)
            self.assertEqual(len(snapshots), 1)
            self.assertEqual(snapshots[0]["row_count"], 3)
            self.assertEqual(
                snapshots[0]["completeness_pct"], 100
            )

    def test_pipeline_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "history.db"

            profile = profile_dataframe(
                pd.DataFrame({"value": [1, 2]})
            )

            save_snapshot("api_a", profile, db_path)
            save_snapshot("api_b", profile, db_path)

            a = get_latest_snapshots(
                "api_a", db_path=db_path
            )
            b = get_latest_snapshots(
                "api_b", db_path=db_path
            )

            self.assertEqual(len(a), 1)
            self.assertEqual(len(b), 1)

    def test_snapshot_ordering(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "history.db"

            first = profile_dataframe(
                pd.DataFrame({"value": [1, 2]})
            )

            second = profile_dataframe(
                pd.DataFrame({"value": [1, 2, 3, 4]})
            )

            save_snapshot("test_api", first, db_path)
            save_snapshot("test_api", second, db_path)

            snapshots = get_latest_snapshots(
                "test_api", limit=2, db_path=db_path
            )

            self.assertEqual(
                [s["row_count"] for s in snapshots],
                [4, 2]
            )


if __name__ == "__main__":
    unittest.main()
