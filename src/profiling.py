import pandas as pd


def profile_dataframe(df):
    """Generate a reusable statistical profile for any DataFrame."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")

    rows, columns = df.shape

    overview = {
        "rows": rows,
        "columns": columns,
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_pct": round(
            df.duplicated().mean() * 100, 2
        ) if rows else 0,
        "missing_cells": int(df.isna().sum().sum()),
        "completeness_pct": round(
            (1 - df.isna().sum().sum() / (rows * columns))
            * 100, 2
        ) if rows and columns else 0,
        "memory_kb": round(
            df.memory_usage(deep=True).sum() / 1024, 2
        ),
    }

    column_profiles = []
    numeric_profiles = []
    category_profiles = []

    for column in df.columns:
        series = df[column]
        non_null = series.dropna()
        missing = int(series.isna().sum())

        column_profiles.append({
            "column": column,
            "dtype": str(series.dtype),
            "missing_count": missing,
            "missing_pct": round(
                missing / rows * 100, 2
            ) if rows else 0,
            "unique_count": int(series.nunique(dropna=True)),
        })

        if pd.api.types.is_numeric_dtype(series) and not (
            pd.api.types.is_bool_dtype(series)
        ):
            values = pd.to_numeric(
                series, errors="coerce"
            ).dropna()

            if values.empty:
                continue

            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1

            if iqr > 0:
                outliers = (
                    (values < q1 - 1.5 * iqr) |
                    (values > q3 + 1.5 * iqr)
                )
                outlier_count = int(outliers.sum())
            else:
                outlier_count = 0

            numeric_profiles.append({
                "column": column,
                "count": len(values),
                "mean": float(values.mean()),
                "median": float(values.median()),
                "std_dev": (
                    float(values.std()) if len(values) > 1
                    else 0.0
                ),
                "min": float(values.min()),
                "q1": float(q1),
                "q3": float(q3),
                "max": float(values.max()),
                "outlier_count": outlier_count,
                "outlier_pct": round(
                    outlier_count / len(values) * 100, 2
                ),
            })

        elif (
            pd.api.types.is_object_dtype(series)
            or isinstance(series.dtype, pd.CategoricalDtype)
            or pd.api.types.is_bool_dtype(series)
        ):
            counts = non_null.astype(str).value_counts().head(5)

            for value, count in counts.items():
                category_profiles.append({
                    "column": column,
                    "value": value,
                    "count": int(count),
                    "pct": round(
                        count / rows * 100, 2
                    ) if rows else 0,
                })

    return {
        "overview": overview,
        "columns": pd.DataFrame(column_profiles),
        "numeric": pd.DataFrame(numeric_profiles),
        "categories": pd.DataFrame(category_profiles),
    }
