import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def build_report(pipeline_name, monitoring, output_dir="outputs"):
    """Generate JSON, Markdown, and Excel monitoring reports."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    status = monitoring["status"]
    alerts = monitoring["alerts"]
    summary = monitoring.get("summary", {})

    payload = {
        "pipeline": pipeline_name,
        "generated_at": timestamp,
        "status": status,
        "alert_count": len(alerts),
        "summary": summary,
        "alerts": alerts,
    }

    # JSON report
    json_path = output_dir / f"{pipeline_name}_monitoring.json"
    json_path.write_text(
        json.dumps(payload, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    # Markdown report
    md_path = output_dir / f"{pipeline_name}_monitoring.md"

    lines = [
        f"# Data Quality Report — {pipeline_name}",
        "",
        f"**Generated:** {timestamp}",
        f"**Status:** {status.upper()}",
        f"**Alerts:** {len(alerts)}",
        "",
        "## Dataset comparison",
        "",
        "| Metric | Previous | Current |",
        "|---|---:|---:|",
        f"| Records | {summary.get('previous_rows', 'N/A')} | "
        f"{summary.get('current_rows', 'N/A')} |",
        f"| Completeness (%) | "
        f"{summary.get('previous_completeness', 'N/A')} | "
        f"{summary.get('current_completeness', 'N/A')} |",
        "",
        "## Detected anomalies",
        "",
    ]

    if not alerts:
        lines.append("No anomalies detected.")
    else:
        lines.extend([
            "| Severity | Check | Description |",
            "|---|---|---|",
        ])

        for alert in alerts:
            message = str(alert["message"]).replace("|", "\\|")
            lines.append(
                f"| {alert['severity'].upper()} | "
                f"{alert['code']} | {message} |"
            )

    md_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    # Excel report
    wb = Workbook()
    overview = wb.active
    overview.title = "Overview"

    overview.append(["API DATA QUALITY REPORT", pipeline_name])
    overview.append(["Generated", timestamp])
    overview.append(["Status", status.upper()])
    overview.append(["Alerts", len(alerts)])
    overview.append([])
    overview.append(["Metric", "Previous", "Current"])
    overview.append([
        "Records",
        summary.get("previous_rows"),
        summary.get("current_rows"),
    ])
    overview.append([
        "Completeness (%)",
        summary.get("previous_completeness"),
        summary.get("current_completeness"),
    ])

    alert_sheet = wb.create_sheet("Alerts")
    alert_sheet.append([
        "Severity", "Code", "Description",
        "Previous", "Current",
    ])

    for alert in alerts:
        alert_sheet.append([
            alert["severity"].upper(),
            alert["code"],
            alert["message"],
            str(alert["previous"]),
            str(alert["current"]),
        ])

    # Formatting
    navy = "17365D"
    white = "FFFFFF"

    for ws in wb.worksheets:
        ws.freeze_panes = "A2"

        header_row = 6 if ws.title == "Overview" else 1

        for cell in ws[header_row]:
            cell.fill = PatternFill(
                "solid", fgColor=navy
            )
            cell.font = Font(
                bold=True, color=white
            )

        for column in ws.columns:
            letter = get_column_letter(
                column[0].column
            )

            max_length = max(
                len(str(cell.value or ""))
                for cell in column
            )

            ws.column_dimensions[letter].width = min(
                max(max_length + 3, 14), 65
            )

        for row in ws:
            for cell in row:
                cell.alignment = Alignment(
                    vertical="center"
                )

    excel_path = output_dir / f"{pipeline_name}_monitoring.xlsx"
    wb.save(excel_path)

    return {
        "json": json_path,
        "markdown": md_path,
        "excel": excel_path,
    }
