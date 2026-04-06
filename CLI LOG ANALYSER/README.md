# CLI Log Analyzer

A command-line tool to analyze Nginx/Apache server logs with real-time monitoring.

## Features

- Parse Nginx/Apache combined log format
- Analyze error rates, top IPs, endpoints, peak hours
- Color-coded terminal reports using `rich`
- Export reports to JSON and CSV
- Real-time log watching with error spike alerts

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Analyze a log file
```bash
python -m log_analyzer.cli analyze sample_logs/access.log
python -m log_analyzer.cli analyze sample_logs/access.log --format json --output report.json
python -m log_analyzer.cli analyze sample_logs/access.log --format csv --output report.csv
```

### Generate sample logs
```bash
python -m log_analyzer.cli generate sample_logs/access.log --lines 1000
```

### Watch a log file in real time
```bash
python -m log_analyzer.cli watch sample_logs/access.log --threshold 5 --window 30
```

## Stack

- Python 3.11+
- rich — terminal formatting
- pytest — testing

## Project Structure
```
log_analyzer/
├── models.py      # Dataclasses
├── parser.py      # Log parsing
├── analyzer.py    # Analysis engine
├── reporter.py    # Rich terminal output
├── exporter.py    # JSON + CSV export
├── watcher.py     # Real-time monitoring
├── generator.py   # Sample log generator
└── cli.py         # CLI entry point
```