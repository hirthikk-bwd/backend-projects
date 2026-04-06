import pytest
from datetime import datetime, timezone
from log_analyzer.models import LogEntry
from log_analyzer.analyzer import analyze


def make_entry(
    status_code: int, ip: str = "192.168.1.1", path: str = "/api/test"
) -> LogEntry:
    """Helper to create a LogEntry for testing."""
    return LogEntry(
        ip=ip,
        timestamp=datetime.now(timezone.utc),
        method="GET",
        path=path,
        protocol="HTTP/1.1",
        status_code=status_code,
        response_size=100,
        referer="-",
        user_agent="curl/7.68.0",
    )


def test_total_requests():
    """Test total requests count."""
    entries = [make_entry(200), make_entry(404), make_entry(500)]
    result = analyze(entries)
    assert result.total_requests == 3


def test_error_rate():
    """Test error rate calculation."""
    entries = [make_entry(200), make_entry(200), make_entry(500), make_entry(404)]
    result = analyze(entries)
    assert result.error_rate == 50.0


def test_empty_entries():
    """Test that empty entries return safe defaults."""
    result = analyze([])
    assert result.total_requests == 0
    assert result.error_rate == 0.0


def test_top_ips():
    """Test top IPs are sorted by counts."""
    entries = [
        make_entry(200, ip="10.0.0.1"),
        make_entry(200, ip="10.0.0.1"),
        make_entry(200, ip="10.0.0.2"),
    ]
    result = analyze(entries)
    assert result.top_ips[0][0] == "10.0.0.1"
    assert result.top_ips[0][1] == 2
