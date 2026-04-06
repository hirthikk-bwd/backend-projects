import argparse
from pathlib import Path
from log_analyzer.parser import parse_file
from log_analyzer.analyzer import analyze
from log_analyzer.reporter import print_report
from log_analyzer.exporter import export_json, export_csv
from log_analyzer.generator import generate_log_file


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="CLI Log Analyzer - analyze Nginx/Apache Logs"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a log file")
    analyze_parser.add_argument("filepath", type=Path, help="Path to log file")
    analyze_parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top items"
    )
    analyze_parser.add_argument(
        "--format", choices=["terminal", "json", "csv"], default="terminal"
    )
    analyze_parser.add_argument("--output", type=Path, help="Output file path")

    # generate subcommand
    generate_parser = subparsers.add_parser("generate", help="Generate sample log file")
    generate_parser.add_argument("filepath", type=Path, help="Output file path")
    generate_parser.add_argument(
        "--lines", type=int, default=1000, help="Number of lines"
    )

    # watch subcommand
    watch_parser = subparsers.add_parser("watch", help="Watch log file in real time")
    watch_parser.add_argument("filepath", type=Path, help="Path to log file")
    watch_parser.add_argument("--threshold", type=int, default=10)
    watch_parser.add_argument("--window", type=int, default=60)
    watch_parser.add_argument("--interval", type=float, default=1.0)

    args = parser.parse_args()

    if args.command == "analyze":
        entries = parse_file(args.filepath)
        result = analyze(entries, top_n=args.top_n)

        if args.format == "terminal":
            print_report(result)
        elif args.format == "json":
            output = args.output or Path("report.json")
            export_json(result, output)
            print(f"Report saved to {output}")
        elif args.format == "csv":
            output = args.output or Path("report.csv")
            export_csv(result, output)
            print(f"Report saved to {output}")

    elif args.command == "generate":
        generate_log_file(args.filepath, lines=args.lines)

    elif args.command == "watch":
        from log_analyzer.watcher import watch_file

        watch_file(args.filepath, args.threshold, args.window, args.interval)


if __name__ == "__main__":
    main()
