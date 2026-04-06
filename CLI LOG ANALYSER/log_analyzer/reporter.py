from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from log_analyzer.models import AnalysisResult

console = Console()


def print_summary(result: AnalysisResult) -> None:
    """Print a summary panel with key metrics."""
    start, end = result.time_range
    start_str = start.strftime("%b %d %H:%M") if start else "N/A"
    end_str = end.strftime("%b %d %H:%M") if end else "N/A"

    summary = (
        f"Total Requests:  {result.total_requests:,}\n"
        f"Error Rate:      {result.error_rate}%\n"
        f"Time Range:      {start_str} - {end_str}\n"
        f"Avg Response:    {result.avg_response_size:,} bytes"
    )
    console.print(Panel(summary, title="LOG ANALYSIS REPORT", style="bold blue"))


def print_status_codes(result: AnalysisResult) -> None:
    """Print status code distribution table with color coding."""
    table = Table(title="Status Code Distribution")
    table.add_column("Status", style="bold")
    table.add_column("Count")
    table.add_column("Percentage")

    for code, count in sorted(result.status_code_counts.items()):
        percentage = count / result.total_requests * 100
        pct_str = f"{percentage:.1f}%"

        if code < 300:
            style = "green"
        elif code < 400:
            style = "yellow"
        elif code < 500:
            style = "red"
        else:
            style = "bold red"

        table.add_row(
            Text(str(code), style=style),
            Text(str(count), style=style),
            Text(pct_str, style=style),
        )
    console.print(table)


def print_top_ips(result: AnalysisResult) -> None:
    """Print top IP addresses by request count."""
    table = Table(title="Top IP Addresses")
    table.add_column("IP Address", style="cyan")
    table.add_column("Requests", style="bold")

    for ip, count in result.top_ips:
        table.add_row(ip, str(count))

    console.print(table)


def print_top_endpoints(result: AnalysisResult) -> None:
    """Print top endpoints by request count."""
    table = Table(title="Top Endpoints")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Requests", style="bold")

    for endpoint, count in result.top_endpoints:
        table.add_row(endpoint, str(count))

    console.print(table)


def print_report(result: AnalysisResult) -> None:
    """Print the full analysis report."""
    print_summary(result)
    print_status_codes(result)
    print_top_ips(result)
    print_top_endpoints(result)
