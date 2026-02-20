"""
core/reporter.py
Saves benchmark results to JSON files.
"""

import json
import datetime
from pathlib import Path


def save_results(results: dict, output_dir: str = "./results") -> str:
    """Save results as a JSON file. Returns the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Build a descriptive filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_slug = results["model"].replace(":", "-").replace("/", "-")
    gpu_slug = results["hardware"]["gpu"].replace(" ", "_")[:30]

    filename = f"{model_slug}__{gpu_slug}__{timestamp}.json"
    filepath = Path(output_dir) / filename

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)

    # Print a clean summary table
    _print_summary(results)

    print(f"\n Full results saved to: {filepath}")
    return str(filepath)


def _print_summary(results: dict):
    hw = results["hardware"]
    summary = results["summary"]

    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY")
    print("=" * 50)
    print(f"Model:   {results['model']}")
    print(f"Backend: {results['backend']}")
    print(f"CPU:     {hw['cpu']}")
    print(f"GPU:     {hw['gpu']}")
    print(f"RAM:     {hw['ram_gb']} GB")
    print(f"OS:      {hw['os']}")
    print("-" * 50)
    print(f"Avg tokens/sec:  {summary['overall_avg_tokens_per_second']}")
    print(f"Min tokens/sec:  {summary['overall_min_tokens_per_second']}")
    print(f"Max tokens/sec:  {summary['overall_max_tokens_per_second']}")
    print("-" * 50)
    print("Per-prompt breakdown:")
    for r in results["results"]:
        agg = r["aggregate"]
        print(f"  [{r['category']:10}] {r['prompt_id']:20} "
              f"{agg['tokens_per_second_avg']:6.1f} tok/s  "
              f"TTFT: {agg['time_to_first_token_avg_ms']:.0f}ms")
    print("=" * 50)
