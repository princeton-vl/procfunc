#!/usr/bin/env python3
"""Format chat.json files for readable output."""

import argparse
import json
from pathlib import Path


def format_chat(chat_data: list) -> str:
    """Format chat data into readable text."""
    output = []

    for entry in chat_data:
        round_num = entry.get("round", "?")
        output.append(f"{'='*80}")
        output.append(f"ROUND {round_num}")
        output.append(f"{'='*80}")

        if "prompt" in entry:
            output.append("")
            output.append("--- PROMPT ---")
            output.append("")
            output.append(entry["prompt"])

        if "response" in entry:
            output.append("")
            output.append("--- RESPONSE ---")
            output.append("")
            output.append(entry["response"])

        if "error" in entry:
            output.append("")
            output.append("--- ERROR ---")
            output.append("")
            output.append(entry["error"])

        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Format chat.json for readable output")
    parser.add_argument("input", type=Path, help="Input chat.json file")
    parser.add_argument("output", type=Path, help="Output txt file")
    args = parser.parse_args()

    with open(args.input) as f:
        chat_data = json.load(f)

    formatted = format_chat(chat_data)

    with open(args.output, "w") as f:
        f.write(formatted)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
