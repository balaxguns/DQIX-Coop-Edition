#!/usr/bin/env python3
"""Install a creation-time vocation choice on top of the DQIX-Coop native menu.

The original character appearance UI and Guardian prologue remain unchanged.
When starting a blank game, the frontend offers the six starter vocations and
stores the choice. The save-chip callback applies it only to an eligible first
Minstrel save, and then restarts the game. No ROM or save data is embedded.
"""
from pathlib import Path
import argparse
import sys

START_OLD = "/* First eligible fresh Minstrel boot:"
END_OLD = "\nstatic void do_action(int id) {"
FRAME_CALL = "    coop_vocation_prompt_once();"
BOOT_POINT = "    if (g_opt.dlc) backup_unlock_dlc();"
FLUSH_POINT = "void backup_flush(void) {\n"
FLUSH_COMPLETE = "    g_backup_dirty = 0;\n}\n"
CARD_DECL_ANCHOR = "void backup_init(const char* path) {"
CARD_CODE_ANCHOR = "const char* backup_path(void) { return g_backup_path; }"

CARD_CODE = r"""
/* DQIX-Coop creation choice lives OUTSIDE the save during the Guardian
 * storyline. Never modify a save until the two original adventurer slots
 * satisfy the same validator as the tested Python prototype.
 *
 * The pending choice is a tiny local text file beside dqix.sav. It contains
 * only one known vocation name and no user/game metadata.
 */
#define COOP_PENDING_FILE "dqix-coop-start-vocation.txt"
static int g_coop_pending_written, g_coop_restart_ready;

static int coop_vocation_name(const char* name) {
    static const char* allowed[] = {
        "warrior", "martial-artist", "mage", "priest", "thief"
    };
    if (!name) return 0;
    for (int i = 0; i < 5; ++i)
        if (!strcmp(name, allowed[i])) return 1;
    return 0;
}
static int coop_pending_name(char* out, size_t n) {
    FILE* f = fopen(COOP_PENDING_FILE, "rb");
    if (!f) return 0;
    char buffer[32] = {0};
    size_t size = fread(buffer, 1, sizeof buffer, f);
    fclose(f);
    if (size == 0 || size >= sizeof buffer) return 0;
    buffer[size] = 0;
    if (size && buffer[size - 1] == '\n') buffer[--size] = 0;
    if (!coop_vocation_name(buffer) || n <= size) return 0;
    memcpy(out, buffer, size + 1);
    return 1;
}
int dqix_coop_creation_pending(void) {
    char name[32];
    return coop_pending_name(name, sizeof name);
}
int dqix_coop_creation_set(const char* choice) {
    if (choice && !strcmp(choice, "minstrel")) {
        /* Explicit original-class choice: cancel any previous pending choice. */
        if (!dqix_coop_creation_pending()) return 1;
        return remove(COOP_PENDING_FILE) == 0;
    }
    if (!coop_vocation_name(choice)) return 0;
    FILE* f = fopen(COOP_PENDING_FILE, "wb");
    if (!f) return 0;
    int success = fprintf(f, "%s\n", choice) > 0;
    if (fclose(f)) success = 0;
    return success;
}
int dqix_coop_creation_blank(void) {
    if (g_backup_size != 65536u) return 0;
    for (int slot = 0; slot < 2; ++slot) {
        const unsigned char* b = g_backup + (size_t)slot * 32768u;
        if (!memcmp(b, "DRAGON QUEST IX", 15) && (b[21] & 1u))
            return 0;
    }
    return 1;
}
/* Invoked BEFORE the save flush is written; a rejected/partial save is left
 * alone, including during the compulsory Guardian battle.
 */
static void dqix_coop_creation_apply_before_flush(void) {
    if (g_coop_pending_written || g_backup_size != 65536u) return;
    char name[32];
    if (!coop_pending_name(name, sizeof name)) return;
    if (dqix_apply_start_vocation(g_backup, g_backup_size, name) != 1) return;
    g_backup_dirty = 1;
    g_coop_pending_written = 1;
    fprintf(stderr, "[DQIX-Coop] First adventurer save detected: %s\n", name);
}
int dqix_coop_creation_needs_restart(void) {
    int result = g_coop_restart_ready;
    g_coop_restart_ready = 0;
    return result;
}
void dqix_coop_creation_boot_complete(void) {
    /* A pending selection applied before the game begins needs no restart. */
    g_coop_restart_ready = 0;
}
"""

FRONTEND_CODE = r"""/* The initial creation choice is shown on the PC game's first new-game
 * launch, before the original DS appearance customization. During the
 * Guardian prologue it remains pending; on the first eligible Minstrel save
 * the runtime applies it and restarts. This is NOT a reskin of the DS UI.
 */
int dqix_coop_creation_blank(void);
int dqix_coop_creation_pending(void);
int dqix_coop_creation_set(const char* choice);
int dqix_coop_creation_needs_restart(void);
void dqix_coop_creation_boot_complete(void);
static void coop_creation_tick(void) {
    static int asked;
    if (!asked && !g_headless && g_win && !session_requested()) {
        asked = 1;
        if (dqix_coop_creation_blank() && !dqix_coop_creation_pending()) {
            static const char* const labels[6] = {
                "Warrior", "Martial Artist", "Mage", "Priest", "Thief", "Minstrel"
            };
            static const char* keys[6] = {
                "warrior", "martial-artist", "mage", "priest", "thief", "minstrel"
            };
            int choice = choose("Create your hero: starting vocation",
                "Choose a vocation for your new hero.\n\n"
                "You will still play the Guardian prologue normally. "
                "Your choice takes effect when you first become a Level 1 "
                "adventurer, after saving. Minstrel retains the original game.",
                labels, 6, 5, 5);
            if (choice >= 0 && choice <= 5) {
                if (!dqix_coop_creation_set(keys[choice]))
                    info_box(SDL_MESSAGEBOX_ERROR, "Starting vocation",
                        "Could not save your starting vocation selection. "
                        "The game's original Minstrel path remains available.",
                        g_win);
            }
        }
    }
    if (dqix_coop_creation_needs_restart()) {
        info_box(SDL_MESSAGEBOX_INFORMATION, "Your new vocation",
            "Your selected vocation is now saved. The game will restart "
            "to load your adventurer with the correct stats and spells.",
            g_win);
        restart_with(NULL);
    }
}
"""


def change_source(contents):
    card = contents["runtime/card.c"]
    front = contents["runtime/frontend_sdl.c"]
    if "dqix_coop_creation_blank" in card:
        if "coop_creation_tick(void)" in front:
            return {}
        raise ValueError("Found only part of the creation patch")
    for code, token in [(card, FLUSH_POINT), (card, FLUSH_COMPLETE),
                        (card, CARD_CODE_ANCHOR), (card, CARD_DECL_ANCHOR),
                        (front, START_OLD), (front, END_OLD),
                        (front, FRAME_CALL), (front, BOOT_POINT)]:
        if code.count(token) != 1:
            raise ValueError("Unexpected DQIX Enhanced source structure; no files changed")

    # Defined after backup_init, so declare the flush callback before using it.
    card = card.replace(
        CARD_DECL_ANCHOR,
        "static void dqix_coop_creation_apply_before_flush(void);\n"
        + CARD_DECL_ANCHOR, 1)
    card = card.replace(FLUSH_POINT,
                        FLUSH_POINT +
                        "    dqix_coop_creation_apply_before_flush();\n", 1)
    card = card.replace(FLUSH_COMPLETE,
        "    g_backup_dirty = 0;\n"
        "    if (g_coop_pending_written) {\n"
        "        /* Remove selection only after successfully writing the save. */\n"
        "        if (!remove(COOP_PENDING_FILE)) {\n"
        "            g_coop_pending_written = 0;\n"
        "            g_coop_restart_ready = 1;\n"
        "        }\n"
        "    }\n}\n", 1)
    # Declarations must precede their use at backup_flush.
    card = card.replace(
        CARD_DECL_ANCHOR,
        "#define COOP_PENDING_FILE \"dqix-coop-start-vocation.txt\"\n"
        "static int g_coop_pending_written, g_coop_restart_ready;\n"
        + CARD_DECL_ANCHOR, 1)
    # CARD_CODE includes the same defines, so keep one set.
    card = card.replace(CARD_CODE_ANCHOR, CARD_CODE + "\n" + CARD_CODE_ANCHOR, 1)
    card = card.replace(
        "#define COOP_PENDING_FILE \"dqix-coop-start-vocation.txt\"\n"
        "static int g_coop_pending_written, g_coop_restart_ready;\n\n"
        "static int coop_vocation_name",
        "static int coop_vocation_name", 1)
    start = front.index(START_OLD)
    end = front.index(END_OLD, start)
    front = front[:start] + FRONTEND_CODE + front[end:]
    front = front.replace(FRAME_CALL, "    coop_creation_tick();", 1)
    front = front.replace(
        "void frontend_init(int argc, char** argv) {",
        "void dqix_coop_creation_boot_complete(void);\n"
        "void frontend_init(int argc, char** argv) {", 1)
    front = front.replace(
        BOOT_POINT,
        BOOT_POINT + "\n    /* Resolve any pending character-creation choice before DS boot. */\n"
        "    backup_flush();\n"
        "    dqix_coop_creation_boot_complete();", 1)
    return {"runtime/card.c": card, "runtime/frontend_sdl.c": front}


def install(root):
    names = ("runtime/card.c", "runtime/frontend_sdl.c")
    original = {}
    for name in names:
        path = root / name
        if not path.is_file():
            raise ValueError("Missing DQIX Enhanced source: " + str(path))
        original[name] = path.read_text(encoding="utf-8")
    updated = change_source(original)
    if not updated:
        return "Character-creation vocation menu already installed"
    for name in names:
        path = root / (name + ".dqix-coop-creation-backup")
        if path.exists():
            raise ValueError("Backup exists but creation patch is incomplete: " + str(path))
    for name in names:
        (root / (name + ".dqix-coop-creation-backup")).write_text(
            original[name], encoding="utf-8")
    try:
        for name in names:
            (root / name).write_text(updated[name], encoding="utf-8")
    except OSError:
        for name in names:
            (root / name).write_text(original[name], encoding="utf-8")
        raise
    return "Installed character-creation vocation selector and deferred save application"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    args = p.parse_args(argv)
    try:
        print(install(args.source))
        return 0
    except (OSError, ValueError) as error:
        p.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
