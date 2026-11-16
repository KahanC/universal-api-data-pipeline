import pandas as pd


class DataValidationError(Exception):
    pass


def validate_dataframe(df, rules):
    """
    Validate a DataFrame using configurable quality rules.

    Supported:
      - required_columns
      - not_null
      - unique
      - min_rows
      - non_negative
    """
    errors = []

    required = rules.get("required_columns", [])

    for column in required:
        if column not in df.columns:
            errors.append(f"Missing required column: {column}")

    for column in rules.get("not_null", []):
        if column not in df.columns:
            errors.append(f"Missing column for not_null: {column}")
        elif df[column].isna().any():
            count = int(df[column].isna().sum())
            errors.append(
                f"{column}: {count} null values"
            )

    unique_columns = rules.get("unique", [])

    if unique_columns:
        missing = [
            col for col in unique_columns
            if col not in df.columns
        ]

        if missing:
            errors.append(
                f"Missing unique columns: {missing}"
            )
        elif df.duplicated(
            subset=unique_columns
        ).any():
            count = int(
                df.duplicated(
                    subset=unique_columns
                ).sum()
            )
            errors.append(
                f"{count} duplicate records "
                f"for {unique_columns}"
            )

    min_rows = rules.get("min_rows", 1)

    if len(df) < min_rows:
        errors.append(
            f"Expected at least {min_rows} rows, "
            f"received {len(df)}"
        )

    for column in rules.get("non_negative", []):
        if column not in df.columns:
            errors.append(
                f"Missing non_negative column: {column}"
            )
            continue

        values = pd.to_numeric(
            df[column], errors="coerce"
        )

        invalid = values.isna() | (values < 0)

        if invalid.any():
            errors.append(
                f"{column}: {int(invalid.sum())} "
                "invalid or negative values"
            )

    if errors:
        raise DataValidationError(
            "Data validation failed:\n- "
            + "\n- ".join(errors)
        )

    return {
        "status": "passed",
        "rows": len(df),
        "checks": len(rules),
    }
