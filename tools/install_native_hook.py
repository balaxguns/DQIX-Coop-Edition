#!/usr/bin/env python3
"""Install the opt-in native vocation hook into YOUR LOCAL DQIX Enhanced source.

Does not alter ROMs or game saves. Makes a backup of runtime/card.c and only
patches a precisely matched upstream function body. Re-run is idempotent.
"""
import argparse
from pathlib import Path
import shutil
import sys

START_MARKER = "void backup_init(const char* path) {"
END_MARKER = "    g_backup_at_boot = malloc(g_backup_size);"
HOOK = """    /* DQIX-Coop-Edition (experimental): apply only on explicit opt-in.
     * Always use a disposable copy of the installation/save for testing.
     * Rejected candidates are never modified.
     */
    const char* coop_requested = getenv("DQIX_START_VOCATION");
    if (coop_requested && *coop_requested) {
        int coop_result = dqix_apply_start_vocation(g_backup, g_backup_size, coop_requested);
        if (coop_result > 0) {
            g_backup_dirty = 1;
            fprintf(stderr, "[DQIX-Coop] Chose starting vocation %s in the loaded test save.\\n",
                    coop_requested);
        } else if (coop_result < 0) {
            fprintf(stderr, "[DQIX-Coop] Save not eligible for vocation change; unchanged.\\n");
        }
    }
"""
PROTOTYPE = "int dqix_apply_start_vocation(unsigned char* image, size_t size, const char* requested);\n"


def install(root, source):
    runtime = root / "runtime"
    card = runtime / "card.c"
    dest = runtime / "dqix_vocation.c"
    if not card.is_file():
        raise ValueError(f"Not a DQIX Enhanced source folder: missing {card}")
    if not source.is_file():
        raise ValueError(f"Hook source file not found: {source}")
    original = card.read_text(encoding="utf-8")
    if HOOK in original and PROTOTYPE in original:
        if not dest.exists() or dest.read_bytes() != source.read_bytes():
            shutil.copyfile(source, dest)
        return "Already installed; hook source is current"
    if "DQIX-Coop-Edition (experimental)" in original:
        raise ValueError("Partly modified card.c detected; refusing to patch")
    if original.count(START_MARKER) != 1 or original.count(END_MARKER) != 1:
        raise ValueError("Unexpected upstream source; no changes made")
    start = original.index(START_MARKER)
    end = original.index(END_MARKER)
    if end <= start:
        raise ValueError("Unexpected backup_init function layout; no changes made")
    # Ensure the insertion point is inside the expected function body.
    if original[start:end].count("}") > 1:
        raise ValueError("Unexpected backup_init structure; no changes made")
    altered = original.replace(START_MARKER, PROTOTYPE + "\n" + START_MARKER, 1)
    altered = altered.replace(END_MARKER, HOOK + END_MARKER, 1)
    backup = runtime / "card.c.dqix-coop-backup"
    if backup.exists():
        raise ValueError(f"Backup already exists but hook is absent: {backup}")
    # Write the original backup before editing. Never modify proprietary ROM.
    backup.write_text(original, encoding="utf-8")
    try:
        dest.write_bytes(source.read_bytes())
        card.write_text(altered, encoding="utf-8")
    except OSError:
        card.write_text(original, encoding="utf-8")
        raise
    return f"Installed native hook. Original runtime source backed up at {backup}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path, help="Path to extracted DQIX Enhanced SOURCE folder")
    args = parser.parse_args(argv)
    own_repo = Path(__file__).resolve().parents[1]
    source = own_repo / "native" / "dqix_vocation.c"
    try:
        print(install(args.upstream, source))
        return 0
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
