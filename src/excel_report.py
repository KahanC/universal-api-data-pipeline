from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter


def export_excel_report(df, output_path, config, validation, profile=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    headers = list(df.columns)
    ws.append(headers)

    for row in df.itertuples(index=False, name=None):
        clean_row = []

        for value in row:
            if pd.isna(value):
                value = None

            # Prevent API strings from being interpreted
            # as Excel formulas.
            if isinstance(value, str) and value.startswith(
                ("=", "+", "-", "@")
            ):
                value = "'" + value

            clean_row.append(value)

        ws.append(clean_row)

    ws.freeze_panes = "A2"

    last_column = get_column_letter(len(headers))
    last_row = len(df) + 1

    table = Table(
        displayName="PipelineData",
        ref=f"A1:{last_column}{last_row}",
    )

    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )

    ws.add_table(table)

    for col_idx, column in enumerate(ws.columns, start=1):
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )

        ws.column_dimensions[
            get_column_letter(col_idx)
        ].width = min(max(max_length + 3, 14), 45)

    for cell in ws[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    info = wb.create_sheet("Run Info")

    metadata = [
        ("Pipeline", config["name"]),
        ("Source API", config["base_url"]),
        ("Endpoint", config.get("endpoint", "")),
        ("Last Refreshed (UTC)", datetime.now(timezone.utc).isoformat()),
        ("Records Exported", len(df)),
        ("Validation", validation["status"]),
        ("Validation Rules", validation["checks"]),
    ]

    for label, value in metadata:
        info.append([label, value])

    for cell in info["A"]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(
            "solid", fgColor="DCE6F1"
        )

    info.column_dimensions["A"].width = 26
    info.column_dimensions["B"].width = 65

    if profile is not None:
        add_profile_sheet(wb, "Data Quality", profile["columns"])
        add_profile_sheet(wb, "Numeric Statistics", profile["numeric"])
        add_profile_sheet(wb, "Categories", profile["categories"])

        # Keep metadata as the final worksheet.
        wb._sheets.remove(info)
        wb._sheets.append(info)

    wb.save(output_path)

    return output_path


def add_profile_sheet(wb, sheet_name, df):
    """Add a formatted profiling worksheet."""
    ws = wb.create_sheet(sheet_name)

    if df.empty:
        ws.append(["Status"])
        ws.append(["No applicable data"])
        ws.column_dimensions["A"].width = 30
        return

    ws.append(list(df.columns))

    for row in df.itertuples(index=False, name=None):
        clean = []
        for value in row:
            if pd.isna(value):
                value = None
            elif isinstance(value, str) and value.startswith(
                ("=", "+", "-", "@")
            ):
                value = "'" + value
            clean.append(value)
        ws.append(clean)

    ws.freeze_panes = "A2"

    last_col = get_column_letter(len(df.columns))
    last_row = len(df) + 1

    table = Table(
        displayName="Profile" + sheet_name.replace(" ", ""),
        ref=f"A1:{last_col}{last_row}",
    )
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showRowStripes=True,
    )
    ws.add_table(table)

    for col_idx, column in enumerate(ws.columns, 1):
        width = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column
        )
        ws.column_dimensions[
            get_column_letter(col_idx)
        ].width = min(max(width + 3, 14), 45)
