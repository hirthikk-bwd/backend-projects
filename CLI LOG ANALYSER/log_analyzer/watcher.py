import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
from log_analyzer.parser import parse_line
from log_analyzer.models import LogEntry

console = Console()


def is_error(entry: LogEntry) -> bool:
    """Return True if the log entry is a 4xx or 5xx error."""
    return entry.status_code >= 400


def watch_file(
    filepath: Path,
    threshold: int = 10,
    window: int = 60,
    interval: float = 1.0,
) -> None:
    """Watch a log file in real time and alert on error spikes."""
    console.print(f"[bold green]Watching {filepath}...[/bold green]")
    console.print(f"Threshold: {threshold} errors per {window}s | Poll: {interval}s\n")

    recent_entries: deque[LogEntry] = deque()
    total_requests = 0
    total_errors = 0
    alerts_triggered = 0
    start_time = datetime.now(timezone.utc)

    with open(str(filepath), "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        try:
            while True:
                line = f.readline()

                if line:
                    entry = parse_line(line)
                    if entry:
                        total_requests += 1
                        recent_entries.append(entry)
                        if is_error(entry):
                            total_errors += 1

                        # Remove entries outside the time window
                        now = datetime.now(timezone.utc)
                        while (
                            recent_entries
                            and (now - recent_entries[0].timestamp).seconds > window
                        ):
                            recent_entries.popleft()

                        # Count errors in current window
                        error_count = sum(1 for e in recent_entries if is_error(e))

                        # Check threshold
                        if error_count >= threshold:
                            alerts_triggered += 1
                            console.print(
                                f"[bold red]⚠ ALERT: {error_count} errors "
                                f"in {window}s (threshold: {threshold})[/bold red]"
                            )

                        # Live status line
                        console.print(
                            f"[{entry.timestamp.strftime('%H:%M:%S')}] "
                            f"Requests: {total_requests} | "
                            f"Errors in window: {error_count}/{window}s",
                            end="\r",
                        )
                else:
                    time.sleep(interval)

        except KeyboardInterrupt:
            duration = (datetime.now(timezone.utc) - start_time).seconds
            console.print("\n\n[bold]Watch session summary:[/bold]")
            console.print(
                f"  Duration: {duration}s | "
                f"Total requests: {total_requests} | "
                f"Alerts: {alerts_triggered}"
            )
