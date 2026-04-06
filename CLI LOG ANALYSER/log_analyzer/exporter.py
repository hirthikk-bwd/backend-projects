import json
import csv
from pathlib import Path
from log_analyzer.models import AnalysisResult


def export_json(result: AnalysisResult, filepath: Path) -> None:
    """Export analysis result to a JSON file."""
    data = {
        "total_requests": result.total_requests,
        "error_rate": result.error_rate,
        "avg_response_size": result.avg_response_size,
        "status_code_counts": result.status_code_counts,
        "method_distribution": result.method_distribution,
        "top_ips": result.top_ips,
        "top_endpoints": result.top_endpoints,
        "peak_hours": result.peak_hours,
        "time_range": [
            result.time_range[0].isoformat() if result.time_range[0] else None,
            result.time_range[1].isoformat() if result.time_range[1] else None,
        ],
    }
    with filepath.open("w") as f:
        json.dump(data, f, indent=4)


def export_csv(result: AnalysisResult, filepath: Path) -> None:
    """Export analysis result to a CSV file."""
    with filepath.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Requests", result.total_requests])
        writer.writerow(["Error Rate (%)", result.error_rate])
        writer.writerow(["Avg Response Size (bytes)", result.avg_response_size])

        writer.writerow([])
        writer.writerow(["Status Code", "Count"])
        for code, count in result.status_code_counts.items():
            writer.writerow([code, count])

        writer.writerow([])
        writer.writerow(["HTTP Method", "Count"])
        for method, count in result.method_distribution.items():
            writer.writerow([method, count])

        writer.writerow([])
        writer.writerow(["Top IPs"])
        writer.writerow(["IP Address", "Requests"])
        for ip, count in result.top_ips:
            writer.writerow([ip, count])

        writer.writerow([])
        writer.writerow(["Top Endpoints"])
        writer.writerow(["Endpoint", "Requests"])
        for endpoint, count in result.top_endpoints:
            writer.writerow([endpoint, count])

        writer.writerow([])
        writer.writerow(["Peak Hours"])
        writer.writerow(["Hour", "Requests"])
        for hour, count in result.peak_hours:
            writer.writerow([hour, count])
