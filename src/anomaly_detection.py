DEFAULT_THRESHOLDS = {
    "row_drop_pct": 20,
    "row_increase_pct": 50,
    "completeness_drop_pp": 5,
    "duplicate_increase": 0,
}


def detect_anomalies(current, previous, thresholds=None):
    """
    Compare current and previous profiling snapshots.

    Returns a structured monitoring report.
    """
    limits = {
        **DEFAULT_THRESHOLDS,
        **(thresholds or {}),
    }

    alerts = []

    current_overview = current["overview"]
    previous_overview = previous["overview"]

    old_rows = previous_overview["rows"]
    new_rows = current_overview["rows"]

    def add_alert(code, severity, message, old, new):
        alerts.append({
            "code": code,
            "severity": severity,
            "message": message,
            "previous": old,
            "current": new,
        })

    # 1. Record count changes
    if old_rows > 0:
        change_pct = (
            (new_rows - old_rows) / old_rows
        ) * 100

        if change_pct < -limits["row_drop_pct"]:
            add_alert(
                "ROW_COUNT_DROP",
                "high",
                f"Record count decreased {abs(change_pct):.2f}%",
                old_rows,
                new_rows,
            )

        elif change_pct > limits["row_increase_pct"]:
            add_alert(
                "ROW_COUNT_SPIKE",
                "medium",
                f"Record count increased {change_pct:.2f}%",
                old_rows,
                new_rows,
            )

    # 2. Completeness deterioration
    old_complete = previous_overview["completeness_pct"]
    new_complete = current_overview["completeness_pct"]

    drop_pp = old_complete - new_complete

    if drop_pp > limits["completeness_drop_pp"]:
        add_alert(
            "COMPLETENESS_DROP",
            "high",
            f"Completeness declined {drop_pp:.2f} percentage points",
            old_complete,
            new_complete,
        )

    # 3. Duplicate increases
    old_duplicates = previous_overview["duplicate_rows"]
    new_duplicates = current_overview["duplicate_rows"]

    if (
        new_duplicates - old_duplicates
        > limits["duplicate_increase"]
    ):
        add_alert(
            "DUPLICATE_INCREASE",
            "medium",
            "Duplicate row count increased",
            old_duplicates,
            new_duplicates,
        )

    # 4. Schema drift
    old_columns = {
        row["column"] for row in previous["columns"]
    }
    new_columns = {
        row["column"] for row in current["columns"]
    }

    removed = sorted(old_columns - new_columns)
    added = sorted(new_columns - old_columns)

    if removed or added:
        add_alert(
            "SCHEMA_DRIFT",
            "high" if removed else "medium",
            f"Removed columns: {removed}; Added columns: {added}",
            sorted(old_columns),
            sorted(new_columns),
        )

    return {
        "status": "alert" if alerts else "healthy",
        "alert_count": len(alerts),
        "alerts": alerts,
        "summary": {
            "previous_rows": old_rows,
            "current_rows": new_rows,
            "previous_completeness": old_complete,
            "current_completeness": new_complete,
        },
    }
