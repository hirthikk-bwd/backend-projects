import pytest
from log_analyzer.parser import parse_line
from log_analyzer.models import LogEntry

def test_parse_valid_line():
    """Test that a valid log line parses correctly."""
    line = '192.168.1.1 - - [04/Apr/2026:13:55:36 +0530] "GET /api/users HTTP/1.1" 200 2326 "-" "Mozilla/5.0"'
    entry = parse_line(line)

    assert entry is not None
    assert entry.ip == "192.168.1.1"
    assert entry.method == "GET"
    assert entry.path == "/api/users"
    assert entry.status_code == 200
    assert entry.response_size == 2326

def test_parse_invalid_line():
    """Test that an invalid line returns None."""
    entry = parse_line("this is not a log line")
    assert entry is None

def test_parse_empty_line():
    """Test that an empty line returns None."""
    entry = parse_line("")
    assert entry is None

def test_parse_dash_response_size():
    """Test that a dash response size is parsed as 0."""
    line = '192.168.1.1 - - [04/Apr/2026:13:55:36 +0530] "GET /api/users HTTP/1.1" 404 - "-" "curl/7.68.0"'
    entry = parse_line(line)
    assert entry is not None
    assert entry.response_size == 0
    