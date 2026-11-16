import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from validation import validate_dataframe, DataValidationError


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.rules = {
            "required_columns": ["ID", "Amount"],
            "not_null": ["ID"],
            "unique": ["ID"],
            "min_rows": 1,
            "non_negative": ["Amount"],
        }

    def test_valid_data(self):
        df = pd.DataFrame({
            "ID": [1, 2, 3],
            "Amount": [100, 200, 300],
        })

        result = validate_dataframe(df, self.rules)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["rows"], 3)

    def test_duplicate_records(self):
        df = pd.DataFrame({
            "ID": [1, 1],
            "Amount": [100, 200],
        })

        with self.assertRaises(DataValidationError):
            validate_dataframe(df, self.rules)

    def test_missing_values(self):
        df = pd.DataFrame({
            "ID": [1, None],
            "Amount": [100, 200],
        })

        with self.assertRaises(DataValidationError):
            validate_dataframe(df, self.rules)

    def test_negative_amounts(self):
        df = pd.DataFrame({
            "ID": [1, 2],
            "Amount": [100, -50],
        })

        with self.assertRaises(DataValidationError):
            validate_dataframe(df, self.rules)

    def test_missing_required_column(self):
        df = pd.DataFrame({"ID": [1, 2]})

        with self.assertRaises(DataValidationError):
            validate_dataframe(df, self.rules)


if __name__ == "__main__":
    unittest.main()
