import pandas as pd

from api_client import APIClient, extract_records


def test_world_bank():
    print("\n[1] WORLD BANK API")

    client = APIClient(
        "https://api.worldbank.org/v2"
    )

    data = client.get(
        "country/CA;US/indicator/NY.GDP.MKTP.CD",
        params={
            "format": "json",
            "date": "2020:2024",
            "per_page": 100,
        },
    )

    records = extract_records(data, "1")

    df = pd.json_normalize(records)

    print(f"Retrieved {len(df)} GDP records")
    print(df[["country.value", "date", "value"]].head())


def test_json_placeholder():
    print("\n[2] JSONPLACEHOLDER API")

    client = APIClient(
        "https://jsonplaceholder.typicode.com"
    )

    data = client.get("users")

    df = pd.json_normalize(data)

    print(f"Retrieved {len(df)} user records")
    print(df[["name", "email", "address.city"]].head())


if __name__ == "__main__":
    test_world_bank()
    test_json_placeholder()

    print("\nBoth API connectors executed successfully!")
