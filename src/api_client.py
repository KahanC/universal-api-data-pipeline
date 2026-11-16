import os
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    def __init__(
        self,
        base_url,
        auth_type="none",
        token_env=None,
        timeout=60,
    ):
        self.base_url = base_url.rstrip("/")

        # Separate connection and read timeouts
        self.timeout = (10, timeout)

        self.session = requests.Session()

        retry_strategy = Retry(
            total=5,
            connect=5,
            read=5,
            status=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
        )

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        if auth_type != "none":
            if not token_env:
                raise ValueError(
                    "token_env is required for authentication"
                )

            token = os.getenv(token_env)

            if not token:
                raise ValueError(
                    f"Missing environment variable: {token_env}"
                )

            if auth_type == "bearer":
                self.session.headers["Authorization"] = (
                    f"Bearer {token}"
                )

            elif auth_type == "api_key":
                self.session.headers["X-API-Key"] = token

            else:
                raise ValueError(
                    f"Unsupported authentication: {auth_type}"
                )

    def get(self, endpoint="", params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()


def extract_records(data, record_path):
    """
    Extract a list from a nested JSON response.
    Example: record_path = "data.results"
    """
    current = data

    for key in record_path.split("."):
        if isinstance(current, list):
            current = current[int(key)]
        else:
            current = current[key]

    if not isinstance(current, list):
        raise ValueError(
            "Record path must resolve to a list"
        )

    return current
