import random

from datetime import datetime, timedelta

from pathlib import Path



IPS = [

    "192.168.1.1", "192.168.1.2", "10.0.0.1", "10.0.0.2",

    "172.16.0.1", "172.16.0.2", "203.0.113.1", "203.0.113.2",

    "198.51.100.1", "198.51.100.2", "192.0.2.1", "192.0.2.2",

]



ENDPOINTS = [

    "/api/users", "/api/products", "/api/orders", "/api/login",

    "/api/health", "/static/css/app.css", "/static/js/bundle.js",

    "/favicon.ico", "/api/cart", "/api/checkout",

]



METHODS = ["GET", "POST", "PUT", "DELETE"]

METHOD_WEIGHTS = [60, 25, 10, 5]



STATUS_CODES = [200, 301, 304, 400, 401, 403, 404, 500, 503]

STATUS_WEIGHTS = [70, 5, 5, 5, 5, 2, 5, 2, 1]



USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",

    "curl/7.68.0",

    "Python/3.11",

    "Googlebot/2.1",

]



def generate_log_line(timestamp: datetime) -> str:

    """Generate a single realistic log line."""

    ip = random.choice(IPS)

    method = random.choices(METHODS, weights=METHOD_WEIGHTS, k=1)[0]

    endpoint = random.choice(ENDPOINTS)

    status = random.choices(STATUS_CODES, weights=STATUS_WEIGHTS, k=1)[0]

    size = random.randint(100, 5000) if status != 304 else 0

    user_agent = random.choice(USER_AGENTS)

    ts = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0530")

    return f'{ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "{user_agent}"'



def generate_log_file(filepath: Path, lines: int = 1000) -> None:

    """Generate a realistic log file with the given number of lines."""

    start_time = datetime.now() - timedelta(hours=24)

    with filepath.open("w") as f:

        for i in range(lines):

            timestamp = start_time + timedelta(seconds=i * 86)

            line = generate_log_line(timestamp)

            f.write(line + "\n")

    print(f"Generated {lines} log lines -> {filepath}")