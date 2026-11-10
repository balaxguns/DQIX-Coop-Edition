#!/usr/bin/env python3
"""Rank candidate DQIX functions using two DQIX_PROF function-entry reports.

The result is only a debugging shortlist, not evidence that a function
controls character creation or vocations.
"""
import argparse
from pathlib import Path
import re

LINE = re.compile(r"^\s*(\d+)\s+ARM([79])\s+([0-9a-fA-F]{8})\s+(.*?)\s*$")

def parse_profile(path):
    result = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE.match(line)
        if match:
            count, cpu, address, name = match.groups()
            key = (cpu, address.lower())
            existing = result.get(key, (0, ""))[0]
            result[key] = (existing + int(count), name)
    if not result:
        raise ValueError(f"No ARM7/ARM9 profile records found in {path}")
    return result

def compare(baseline, creation, minimum=1, arm9_only=True):
    rows = []
    for (cpu, address), (count, name) in creation.items():
        if arm9_only and cpu != "9":
            continue
        previous = baseline.get((cpu, address), (0, ""))[0]
        delta = count - previous
        if count >= minimum and delta > 0:
            rows.append((delta, count, previous, cpu, address, name))
    return sorted(rows, key=lambda row: (-row[0], -row[1], row[3], row[4]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("creation", type=Path)
    parser.add_argument("--minimum", type=int, default=1)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--include-arm7", action="store_true")
    args = parser.parse_args()
    if args.minimum < 1 or args.top < 1:
        parser.error("--minimum and --top must be positive")
    try:
        rows = compare(parse_profile(args.baseline), parse_profile(args.creation),
                       args.minimum, not args.include_arm7)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Delta  Creation  Baseline  CPU  Address   Function (candidate only)")
    for delta, count, previous, cpu, addr, name in rows[:args.top]:
        print(f"{delta:>5}  {count:>8}  {previous:>8}  ARM{cpu}  {addr}  {name}")

if __name__ == "__main__":
    main()
