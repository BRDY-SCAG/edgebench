#!/usr/bin/env python3
"""
tools/submit.py

Prepares a result JSON for submission to the community database.
Adds metadata, copies to submissions/, then runs update_dashboard.

Usage:
    python tools/submit.py --file results/yourfile.json --username BRDY-SCAG
"""

import json
import argparse
import subprocess
from pathlib import Path

SUBMISSIONS_DIR = Path(__file__).parent.parent / "submissions"


def main():
    parser = argparse.ArgumentParser(description="Submit a benchmark result")
    parser.add_argument("--file", required=True, help="Path to result JSON file")
    parser.add_argument("--username", required=True, help="Your GitHub username")
    args = parser.parse_args()

    result_path = Path(args.file)
    if not result_path.exists():
        print(f"File not found: {result_path}")
        return

    # Load result
    with open(result_path) as f:
        data = json.load(f)

    # Inject submission metadata
    data["meta"] = {
        "submitted_by": args.username,
    }

    # Check for duplicate submissions (same user + model + cpu)
    existing = list(SUBMISSIONS_DIR.glob("*.json"))
    for existing_file in existing:
        try:
            with open(existing_file) as f:
                existing_data = json.load(f)
            same_model = existing_data.get("model") == data.get("model")
            same_user = existing_data.get("meta", {}).get("submitted_by") == args.username
            same_cpu = existing_data.get("hardware", {}).get("cpu") == data.get("hardware", {}).get("cpu")
            if same_model and same_user and same_cpu:
                print(f"  A submission already exists for {args.username} / {data.get('model')} on this CPU.")
                print(f"   Existing file: {existing_file.name}")
                answer = input("   Overwrite with newer results? (y/n): ").strip().lower()
                if answer != "y":
                    print(" Submission cancelled.")
                    return
                existing_file.unlink()
                print("   Old submission removed.\n")
                break
        except Exception:
            continue

    # Save to submissions/ with same filename
    dest = SUBMISSIONS_DIR / result_path.name
    with open(dest, "w") as f:
        json.dump(data, f, indent=2)

    print(f" Copied to submissions/{result_path.name}")
    print(f" Tagged as submitted by: {args.username}\n")

    # Run dashboard updater
    print(" Regenerating README dashboard table...")
    updater = Path(__file__).parent / "update_dashboard.py"
    subprocess.run(["python3", str(updater)], check=True)

    print("\n Done! Now run:")
    print("   git add submissions/ README.md")
    print(f"  git commit -m \"add benchmark: {data.get('model')} on {data['hardware'].get('cpu', 'unknown')[:30]}\"")
    print("   git push")


if __name__ == "__main__":
    main()
