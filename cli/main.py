#!/usr/bin/env python3
"""
edgebench - CLI entry point
Usage: python main.py run
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backends.ollama_backend import OllamaBackend
from core.benchmark import run_benchmark
from core.reporter import save_results


def cmd_run(args):
    print("\n edgebench v0.1")
    print("=" * 40)

    backend = OllamaBackend(model=args.model)

    if not backend.is_available():
        print(f" Ollama is not running or model '{args.model}' is not available.")
        print("   Make sure Ollama is running: ollama serve")
        print(f"   And pull the model: ollama pull {args.model}")
        sys.exit(1)

    print(f" Backend: Ollama")
    print(f" Model:   {args.model}")
    print(f" Runs:    {args.runs}\n")

    results = run_benchmark(backend, runs=args.runs)
    save_results(results, output_dir=args.output)

    print("\n Done! Results saved to:", args.output)


def main():
    parser = argparse.ArgumentParser(
        description="edgebench - local LLM inference benchmarking tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    # 'run' subcommand
    run_parser = subparsers.add_parser("run", help="Run benchmarks")
    run_parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="Ollama model to benchmark (default: llama3.2:3b)"
    )
    run_parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of benchmark runs (default: 3)"
    )
    run_parser.add_argument(
        "--output",
        default="./results",
        help="Output directory for results (default: ./results)"
    )

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
