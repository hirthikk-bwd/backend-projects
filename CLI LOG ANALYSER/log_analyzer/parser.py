from pathlib import Path
from datetime import datetime
from log_analyzer.models import LogEntry
import re

LOG_PATTERN = re.compile(
    r'^(\S+) - - \[(.+?)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "(.*?)" "(.*?)"$'
)


def parse_line(line: str) -> LogEntry | None:
    """Parse a single log line into a LogEntry. Returns None if unparseable."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    timestamp_str = match.group(2)
    timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")

    size_str = match.group(7)
    response_size = int(size_str) if size_str != "-" else 0

    return LogEntry(
        ip=match.group(1),
        timestamp=timestamp,
        method=match.group(3),
        path=match.group(4),
        protocol=match.group(5),
        status_code=int(match.group(6)),
        response_size=response_size,
        referer=match.group(8),
        user_agent=match.group(9),
    )


def parse_file(filepath: Path) -> list[LogEntry]:
    """Parse a log file and return a list of valid LogEntry objects."""
    entries = []
    unparseable = 0

    with filepath.open() as f:
        for line in f:
            entry = parse_line(line)
            if entry:
                entries.append(entry)
            else:
                unparseable += 1

    print(f"Parsed {len(entries)} entries. Skipped {unparseable} unparseable lines.")
    return entries
