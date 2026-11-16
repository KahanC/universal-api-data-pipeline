import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from pagination import fetch_all_pages


class TestPagination(unittest.TestCase):

    def test_world_bank_multiple_pages(self):
        client = Mock()

        client.get.side_effect = [
            [{"pages": 3}, [{"id": 1}, {"id": 2}]],
            [{"pages": 3}, [{"id": 3}, {"id": 4}]],
            [{"pages": 3}, [{"id": 5}]],
        ]

        config = {
            "endpoint": "example",
            "record_path": "1",
            "params": {"per_page": 2},
            "pagination": {
                "strategy": "world_bank",
                "max_pages": 10
            }
        }

        records = fetch_all_pages(client, config)

        self.assertEqual(len(records), 5)
        self.assertEqual(client.get.call_count, 3)

    def test_page_number_pagination(self):
        client = Mock()

        client.get.side_effect = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}],
        ]

        config = {
            "endpoint": "records",
            "record_path": "",
            "pagination": {
                "strategy": "page",
                "page_size": 2,
                "max_pages": 10
            }
        }

        records = fetch_all_pages(client, config)

        self.assertEqual(len(records), 3)
        self.assertEqual(client.get.call_count, 2)

    def test_pagination_limit(self):
        client = Mock()
        client.get.return_value = [{"id": 1}, {"id": 2}]

        config = {
            "endpoint": "records",
            "record_path": "",
            "pagination": {
                "strategy": "page",
                "page_size": 2,
                "max_pages": 2
            }
        }

        with self.assertRaises(RuntimeError):
            fetch_all_pages(client, config)

    def test_no_pagination(self):
        client = Mock()
        client.get.return_value = [{"id": 1}]

        config = {
            "endpoint": "records",
            "record_path": "",
        }

        records = fetch_all_pages(client, config)

        self.assertEqual(len(records), 1)
        self.assertEqual(client.get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
