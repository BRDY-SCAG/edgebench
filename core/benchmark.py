"""
core/benchmark.py
Runs the benchmark loop and collects results.
"""

import statistics
from core.hardware import get_hardware_info


def run_benchmark(backend, runs: int = 3) -> dict:
    """
    Run all benchmark prompts N times and aggregate results.
    Returns a structured result dict ready to be saved as JSON.
    """
    print("Detecting hardware...")
    hardware = get_hardware_info()
    print(f"   CPU:  {hardware['cpu']}")
    print(f"   RAM:  {hardware['ram_gb']} GB")
    print(f"   GPU:  {hardware['gpu']}")
    print(f"   OS:   {hardware['os']}\n")

    prompts = backend.get_prompts()
    prompt_results = []

    for prompt_data in prompts:
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["prompt"]
        category = prompt_data["category"]

        print(f"Benchmarking: [{category}] {prompt_id}")
        run_data = []

        for i in range(runs):
            print(f"   Run {i + 1}/{runs}...", end=" ", flush=True)
            result = backend.infer(prompt_text)
            run_data.append(result)
            print(f"{result['tokens_per_second']:.1f} tok/s  ({result['total_time_ms']:.0f}ms)")

        # Aggregate across runs
        tps_values = [r["tokens_per_second"] for r in run_data]
        ttft_values = [r["time_to_first_token_ms"] for r in run_data]
        total_time_values = [r["total_time_ms"] for r in run_data]

        prompt_results.append({
            "prompt_id": prompt_id,
            "category": category,
            "runs": run_data,
            "aggregate": {
                "tokens_per_second_avg": round(statistics.mean(tps_values), 2),
                "tokens_per_second_min": round(min(tps_values), 2),
                "tokens_per_second_max": round(max(tps_values), 2),
                "tokens_per_second_stdev": round(statistics.stdev(tps_values), 2) if len(tps_values) > 1 else 0,
                "time_to_first_token_avg_ms": round(statistics.mean(ttft_values), 2),
                "total_time_avg_ms": round(statistics.mean(total_time_values), 2),
            }
        })

    # Overall summary across all prompts
    all_tps = [r["aggregate"]["tokens_per_second_avg"] for r in prompt_results]

    print(f"\n Overall average: {statistics.mean(all_tps):.1f} tok/s")

    return {
        "schema_version": "0.1",
        "backend": backend.name,
        "model": backend.model,
        "hardware": hardware,
        "config": {
            "runs_per_prompt": runs,
            "temperature": 0,
            "seed": 42,
            "max_tokens": 128,
        },
        "results": prompt_results,
        "summary": {
            "overall_avg_tokens_per_second": round(statistics.mean(all_tps), 2),
            "overall_min_tokens_per_second": round(min(all_tps), 2),
            "overall_max_tokens_per_second": round(max(all_tps), 2),
        }
    }
