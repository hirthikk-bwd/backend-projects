from collections import Counter, defaultdict


from log_analyzer.models import LogEntry, AnalysisResult


def analyze(entries: list[LogEntry], top_n: int = 10) -> AnalysisResult:
    """Analyze a list of log entries and return an AnalysisResult."""

    total = len(entries)

    status_counts = Counter(e.status_code for e in entries)

    ip_counts = Counter(e.ip for e in entries)

    endpoint_counts = Counter(e.path for e in entries)

    method_counts = Counter(e.method for e in entries)

    error_count = sum(count for code, count in status_counts.items() if code >= 400)

    error_rate = (error_count / total * 100) if total > 0 else 0.0

    hourly_counts = defaultdict(int)

    for e in entries:

        hour_str = e.timestamp.strftime("%Y-%m-%d %H:00")

        hourly_counts[hour_str] += 1

    peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    avg_size = sum(e.response_size for e in entries) / total if total > 0 else 0.0

    timestamps = [e.timestamp for e in entries]

    time_range = (min(timestamps), max(timestamps)) if timestamps else (None, None)

    return AnalysisResult(
        total_requests=total,
        status_code_counts=dict(status_counts),
        error_rate=round(error_rate, 2),
        top_ips=ip_counts.most_common(top_n),
        top_endpoints=endpoint_counts.most_common(top_n),
        peak_hours=peak_hours,
        method_distribution=dict(method_counts),
        avg_response_size=round(avg_size, 2),
        time_range=time_range,
    )
