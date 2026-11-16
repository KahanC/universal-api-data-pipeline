import requests
import pandas as pd
from pathlib import Path

API_URL = (
    "https://api.worldbank.org/v2/country/"
    "CA;US;IN;GB/indicator/NY.GDP.MKTP.CD"
)

OUTPUT = Path("outputs/world_bank_gdp.xlsx")


def fetch_data():
    response = requests.get(
        API_URL,
        params={
            "format": "json",
            "date": "2015:2024",
            "per_page": 500,
        },
        timeout=30,
    )
    response.raise_for_status()

    metadata, records = response.json()

    if not isinstance(records, list):
        raise ValueError("Unexpected API response format")

    print(f"API returned {len(records)} records")
    return records


def transform_data(records):
    rows = []

    for record in records:
        rows.append({
            "Country": record["country"]["value"],
            "Country Code": record["countryiso3code"],
            "Year": int(record["date"]),
            "GDP (USD)": record["value"],
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(
        ["Country", "Year"],
        ascending=[True, False]
    )

    return df


def export_excel(df):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(
        OUTPUT,
        index=False,
        engine="openpyxl",
    )

    print(f"Excel exported to: {OUTPUT}")


def main():
    print("Fetching World Bank GDP data...")

    records = fetch_data()
    df = transform_data(records)

    print("\nPreview:")
    print(df.head(10).to_string(index=False))

    export_excel(df)


if __name__ == "__main__":
    main()
