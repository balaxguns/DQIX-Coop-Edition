#!/usr/bin/env python3
"""Annotate DQIX Enhanced ARM9 profile addresses using upstream symbol maps.

No game files are required. Use config/usa/arm9 from a locally cloned
DQIX Enhanced source tree. The tool deliberately reports ambiguity when
different overlays reuse an address.
"""
import argparse
from pathlib import Path
import re
import sys

SYMBOL = re.compile(
    r"^(\S+)\s+kind:function\((arm|thumb)(?:,size=0x([0-9a-fA-F]+))?[^)]*\)\s+addr:0x([0-9a-fA-F]+)"
)
PROFILE = re.compile(r"^\s*(\d+)\s+ARM([79])\s+([0-9a-fA-F]{8})\s+(.*)$")


def modules(config_dir):
    yield "main", config_dir / "symbols.txt"
    for module in ("itcm", "dtcm"):
        yield module, config_dir / module / "symbols.txt"
    overlays = config_dir / "overlays"
    if overlays.exists():
        for path in sorted(overlays.glob("ov*/symbols.txt")):
            yield path.parent.name, path


def load_symbols(config_dir):
    """Return mapping of function entry address to *every* matching module."""
    index = {}
    for module, path in modules(config_dir):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = SYMBOL.match(line)
            if match:
                name, mode, size, address = match.groups()
                key = int(address, 16)
                index.setdefault(key, []).append((module, name, mode, int(size, 16) if size else None))
    if not index:
        raise ValueError(f"No function symbols found beneath {config_dir}")
    return index


def annotate(profile_path, symbols, limit=50):
    entries = []
    for line in profile_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = PROFILE.match(line)
        if not match:
            continue
        count, cpu, address, reported = match.groups()
        if cpu != "9":
            continue
        address_int = int(address, 16)
        candidates = symbols.get(address_int, [])
        if not candidates:
            label = "UNMAPPED"
        elif len(candidates) == 1:
            mod, name, _, _ = candidates[0]
            label = f"{mod}:{name}"
        else:
            label = "AMBIGUOUS " + ", ".join(f"{mod}:{name}" for mod, name, _, _ in candidates)
        entries.append((int(count), address.lower(), label))
    return sorted(entries, key=lambda v: -v[0])[:limit]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("symbols_dir", type=Path, help="Path to config/usa/arm9")
    p.add_argument("profile", type=Path, help="Text containing DQIX_PROF report")
    p.add_argument("--top", type=int, default=50)
    a = p.parse_args()
    if a.top < 1:
        p.error("--top must be positive")
    try:
        symbols = load_symbols(a.symbols_dir)
        rows = annotate(a.profile, symbols, a.top)
    except (OSError, ValueError) as error:
        p.error(str(error))
    if not rows:
        print("No ARM9 profile records found", file=sys.stderr)
        return 1
    for count, address, label in rows:
        print(f"{count:>9} ARM9 {address} {label}")
    if any(label.startswith("AMBIGUOUS") for _, _, label in rows):
        print("WARNING: overlay address reuse prevents unique attribution from this profile alone", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
