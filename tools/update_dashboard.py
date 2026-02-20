#!/usr/bin/env python3
"""
tools/update_dashboard.py

Reads all JSON files from submissions/ and regenerates
the hardware table in README.md automatically.

Usage:
    python tools/update_dashboard.py
"""

import json
import re
from pathlib import Path

SUBMISSIONS_DIR = Path(__file__).parent.parent / "submissions"
README_PATH = Path(__file__).parent.parent / "README.md"

# Markers in README.md that wrap the auto-generated table
TABLE_START = "<!-- DASHBOARD_START -->"
TABLE_END = "<!-- DASHBOARD_END -->"


def load_submissions() -> list:
    raw = []
    for filepath in sorted(SUBMISSIONS_DIR.glob("*.json")):
        try:
            with open(filepath) as f:
                data = json.load(f)
            # Store filename so we can use it for recency sorting
            data["_filename"] = filepath.name
            raw.append(data)
        except Exception as e:
            print(f"  Skipping {filepath.name}: {e}")

    return deduplicate(raw)


def deduplicate(submissions: list) -> list:
    """
    Keep only the most recent submission per (username, model, cpu, gpu) combo.
    Filenames contain a timestamp so sorting by name gives us recency.
    """
    seen = {}
    for s in submissions:
        hw = s.get("hardware", {})
        meta = s.get("meta", {})

        key = (
            meta.get("submitted_by", "anonymous"),
            s.get("model", "unknown"),
            hw.get("cpu", "unknown"),
            hw.get("gpu", "unknown"),
        )

        # Keep the one with the later filename (timestamp is in the name)
        if key not in seen or s["_filename"] > seen[key]["_filename"]:
            if key in seen:
                print(f"  Duplicate found for {key[0]} / {key[1]} — keeping most recent")
            seen[key] = s

    # Clean up internal field before returning
    results = list(seen.values())
    for s in results:
        s.pop("_filename", None)

    return results


def format_hardware(hw: dict) -> str:
    """Build a readable hardware string from the hardware dict."""
    cpu = hw.get("cpu", "Unknown")
    ram = hw.get("ram_gb", "?")
    gpu = hw.get("gpu", "Unknown")

    # For Apple Silicon, CPU and GPU are the same chip
    if "Apple" in cpu:
        return f"{cpu} ({ram}GB unified)"
    else:
        return f"{cpu} + {gpu} ({ram}GB RAM)"


def build_table(submissions: list) -> str:
    if not submissions:
        return "| *No submissions yet — run edgebench and submit your results!* | | | | |\n"

    header = (
        "| Hardware | Model | Avg tok/s | TTFT (ms) | OS | Submitted by |\n"
        "|---|---|---|---|---|---|\n"
    )

    rows = []
    for s in submissions:
        hw = s.get("hardware", {})
        summary = s.get("summary", {})
        meta = s.get("meta", {})

        hardware_str = format_hardware(hw)
        model = s.get("model", "unknown")
        avg_tps = summary.get("overall_avg_tokens_per_second", "?")
        os_str = hw.get("os", "?")
        submitted_by = meta.get("submitted_by", "anonymous")

        # Calculate average TTFT across all prompts
        results = s.get("results", [])
        ttft_values = [
            r["aggregate"]["time_to_first_token_avg_ms"]
            for r in results
            if "aggregate" in r
        ]
        avg_ttft = round(sum(ttft_values) / len(ttft_values), 1) if ttft_values else "?"

        rows.append(
            f"| {hardware_str} | {model} | {avg_tps} | {avg_ttft} | {os_str} | {submitted_by} |"
        )

    return header + "\n".join(rows) + "\n"


def update_readme(table: str):
    with open(README_PATH, "r") as f:
        content = f.read()

    # Check markers exist
    if TABLE_START not in content or TABLE_END not in content:
        print(" Could not find dashboard markers in README.md")
        print(f"   Make sure these lines exist in your README:\n   {TABLE_START}\n   {TABLE_END}")
        return False

    # Replace everything between the markers
    pattern = re.compile(
        rf"{re.escape(TABLE_START)}.*?{re.escape(TABLE_END)}",
        re.DOTALL
    )
    new_section = f"{TABLE_START}\n{table}{TABLE_END}"
    updated = pattern.sub(new_section, content)

    with open(README_PATH, "w") as f:
        f.write(updated)

    return True


def main():
    print(" edgebench dashboard updater")
    print("=" * 40)

    submissions = load_submissions()
    print(f" Found {len(submissions)} submission(s) in submissions/\n")

    table = build_table(submissions)
    success = update_readme(table)

    if success:
        print(" README.md hardware table updated!")
        print("\nUpdated table:")
        print(table)
    else:
        print("\n To fix this, add these markers to your README.md")
        print("   where you want the hardware table to appear:\n")
        print(f"   {TABLE_START}")
        print("   (table goes here)")
        print(f"   {TABLE_END}")


if __name__ == "__main__":
    main()
