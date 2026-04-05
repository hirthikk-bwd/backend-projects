from dataclasses import dataclass


from datetime import datetime


@dataclass


class LogEntry:


    ip: str


    timestamp: datetime


    method: str


    path: str


    protocol: str


    status_code: int


    response_size: int


    referer: str


    user_agent: str





@dataclass


class AnalysisResult:


    total_requests: int


    status_code_counts: dict[int,int]


    error_rate: float


    top_ips: list[tuple[str, int]]


    top_endpoints: list[tuple[str,int]]


    peak_hours: list[tuple[str,int]]


    method_distribution: dict[str,int]


    avg_response_size: float


    time_range: tuple[datetime,datetime]





@dataclass


class Alert:


    timestamp: datetime


    error_count: int


    threshold: int


    window_seconds: int


    message: str