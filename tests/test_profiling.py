import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from profiling import profile_dataframe


class TestProfiling(unittest.TestCase):

    def test_missing_values(self):
        df = pd.DataFrame({
            "ID": [1, 2, 3],
            "Amount": [100, None, 300],
        })

        result = profile_dataframe(df)

        self.assertEqual(result["overview"]["rows"], 3)
        self.assertEqual(result["overview"]["missing_cells"], 1)
        self.assertAlmostEqual(
            result["overview"]["completeness_pct"],
            83.33,
            places=2
        )

    def test_numeric_statistics(self):
        df = pd.DataFrame({
            "Amount": [10, 20, 30, 40, 50]
        })

        result = profile_dataframe(df)
        stats = result["numeric"].iloc[0]

        self.assertEqual(stats["mean"], 30)
        self.assertEqual(stats["median"], 30)
        self.assertEqual(stats["min"], 10)
        self.assertEqual(stats["max"], 50)

    def test_duplicate_detection(self):
        df = pd.DataFrame({
            "ID": [1, 1, 2],
            "Category": ["A", "A", "B"],
        })

        result = profile_dataframe(df)

        self.assertEqual(
            result["overview"]["duplicate_rows"], 1
        )


if __name__ == "__main__":
    unittest.main()
