#!/usr/bin/env python3
"""Install DQIX-Coop's native menu into a SEPARATE DQIX Enhanced source copy.

Expected upstream code is matched explicitly. Makes backups first and refuses
to edit if any target has drifted. The installer never touches game ROMs/saves.
Run install_native_hook.py first. Re-running is idempotent.
"""
from pathlib import Path
import argparse
import sys

BEGIN = "/* DQIX-Coop: integrated starting-vocation menu */"
DECL = "int dqix_coop_apply_menu_start_vocation(const char* requested);"
MENU_ENUM = """    /* DQIX-Coop: six original starting vocations (not advanced classes). */
    MI_COOP_VOC0 = 360, MI_COOP_VOC1, MI_COOP_VOC2,
    MI_COOP_VOC3, MI_COOP_VOC4, MI_COOP_VOC5,
"""
MENU_ITEMS = """        SUB("Starting &vocation (fresh saves only)"),
            IT(MI_COOP_VOC0, "&Warrior", NULL),
            IT(MI_COOP_VOC1, "Martial &Artist", NULL),
            IT(MI_COOP_VOC2, "&Mage", NULL),
            IT(MI_COOP_VOC3, "&Priest", NULL),
            IT(MI_COOP_VOC4, "&Thief", NULL),
            IT(MI_COOP_VOC5, "M&instrel (original)", NULL),
        END,
        SEP,
"""
CARD = """/* DQIX-Coop: changes only a valid early-save Minstrel; writes after backup.
 * The frontend backs up the original before calling and restarts afterward.
 * Both slot checksums are updated by the native validator.
 */
int dqix_coop_apply_menu_start_vocation(const char* requested) {
    int result = dqix_apply_start_vocation(g_backup, g_backup_size, requested);
    if (result == 1) {
        g_backup_dirty = 1;
        backup_flush();
    }
    return result;
}
/* Non-destructive eligibility probe used once after boot by the selector.
 * Run exactly the same validator against an in-memory COPY, never the save.
 */
int dqix_coop_start_vocation_eligible(void) {
    if (g_backup_size != 65536u) return 0;
    unsigned char* temp = (unsigned char*)malloc(g_backup_size);
    if (!temp) return 0;
    memcpy(temp, g_backup, g_backup_size);
    int result = dqix_apply_start_vocation(temp, g_backup_size, "mage");
    free(temp);
    return result == 1;
}
"""
FRONTEND = """/* DQIX-Coop: menu option is available through the Windows menu bar and
 * the SDL in-game menu. This operates on an early saved Minstrel, not
 * on the Celestial/Guardian storyline or advanced vocation unlocks.
 */
""" + DECL + """
int dqix_coop_start_vocation_eligible(void);
static void coop_start_vocation_action(int id) {
    static const char* choices[6] = {
        "warrior", "martial-artist", "mage", "priest", "thief", "minstrel"
    };
    static const char* names[6] = {
        "Warrior", "Martial Artist", "Mage", "Priest", "Thief", "Minstrel"
    };
    if (id < MI_COOP_VOC0 || id > MI_COOP_VOC5) return;
    if (session_requested()) {
        info_box(SDL_MESSAGEBOX_INFORMATION, "Starting vocation",
            "Leave multiplayer before changing a vocation.", g_win);
        return;
    }
    int choice = id - MI_COOP_VOC0;
    if (choice == 5) {
        info_box(SDL_MESSAGEBOX_INFORMATION, "Minstrel",
            "Minstrel is the original starting vocation; no change is needed.", g_win);
        return;
    }
    char message[700], kept[300];
    snprintf(message, sizeof message,
        "Choose %s as the starting vocation?\\n\\n"
        "This works ONLY on an existing, unprogressed Level 1 Minstrel save "
        "(0 or 7 EXP). It keeps the original Guardian prologue.\\n\\n"
        "The current save is copied to the save-backups folder, and the game "
        "will restart after a successful change. Unsaved progress will be lost.",
        names[choice]);
    if (!ask_yes("Choose starting vocation", message, "Select and restart")) return;
    save_backup_copy(kept, sizeof kept);
    if (!kept[0]) {
        info_box(SDL_MESSAGEBOX_ERROR, "Starting vocation",
            "Could not back up your current save; nothing was changed.", g_win);
        return;
    }
    int changed = dqix_coop_apply_menu_start_vocation(choices[choice]);
    if (changed != 1) {
        info_box(SDL_MESSAGEBOX_INFORMATION, "Starting vocation",
            "This save is not an eligible early Level 1 Minstrel save.\\n\\n"
            "No changes made. For a new adventure, finish the Guardian prologue "
            "and save once as Minstrel before selecting a vocation.", g_win);
        return;
    }
    restart_with(NULL);
}
/* First eligible fresh Minstrel boot: show all six choices automatically.
 * Minstrel is also a valid "continue unchanged" choice.
 * This is shown after the Guardian story, when an actual adventurer save
 * exists, not during the original Celestrian-only prologue.
 */
static void coop_vocation_prompt_once(void) {
    static int asked;
    if (asked || g_headless || !g_win || session_requested()) return;
    asked = 1;
    if (!dqix_coop_start_vocation_eligible()) return;
    static const char* const names[6] = {
        "Warrior", "Martial Artist", "Mage", "Priest", "Thief", "Minstrel"
    };
    int picked = choose("Choose starting vocation",
        "Your new adventurer is ready. Select one of the six original "
        "starting vocations. The game keeps its Guardian prologue; this "
        "selection applies at Level 1. Your test save is backed up and "
        "the game restarts when you confirm.", names, 6, 5, 5);
    if (picked >= 0 && picked <= 4)
        coop_start_vocation_action(MI_COOP_VOC0 + picked);
}
"""

def require_once(text, needle, name):
    if text.count(needle) != 1:
        raise ValueError(f"Upstream {name} changed: expected one exact insertion anchor")
    return text

def changes(existing):
    card, head, items, frontend = (existing[k] for k in
                                  ("runtime/card.c", "runtime/menu.h",
                                   "runtime/menu_items.c", "runtime/frontend_sdl.c"))
    if "dqix_apply_start_vocation(" not in card:
        raise ValueError("Install native hook first (tools/install_native_hook.py)")
    if BEGIN in frontend:
        if "dqix_coop_apply_menu_start_vocation" in card and "MI_COOP_VOC0" in head:
            return {}
        raise ValueError("Incomplete prior installation; refusing to edit")

    require_once(card, "const char* backup_path(void) { return g_backup_path; }", "card.c")
    require_once(head, "    MI_DISCORD = 340,", "menu.h")
    require_once(items, '        SUB("Save &file"),', "menu_items.c")
    require_once(frontend, "static void do_action(int id) {", "frontend_sdl.c")
    require_once(frontend, "    case MI_SAVE_EXPORT: save_export(); break;", "frontend_sdl.c")
    require_once(frontend, "static void save_backup_copy(char* out, size_t n) {", "frontend_sdl.c")
    require_once(frontend, "void frontend_frame(void) {", "frontend_sdl.c")

    card = card.replace("const char* backup_path(void) { return g_backup_path; }",
                        CARD + "\nconst char* backup_path(void) { return g_backup_path; }", 1)
    head = head.replace("    MI_DISCORD = 340,", MENU_ENUM + "    MI_DISCORD = 340,", 1)
    items = items.replace('        SUB("Save &file"),',
                          MENU_ITEMS + '        SUB("Save &file"),', 1)
    # Functions used by the action are defined above do_action.
    frontend = frontend.replace("static void do_action(int id) {",
                                BEGIN + "\n" + FRONTEND + "\nstatic void do_action(int id) {", 1)
    # Show a one-time native six-option dialog on the first eligible boot.
    frontend = frontend.replace(
        "void frontend_frame(void) {",
        "void frontend_frame(void) {\\n    coop_vocation_prompt_once();", 1)
    frontend = frontend.replace("    case MI_SAVE_EXPORT: save_export(); break;",
                                "    case MI_COOP_VOC0: case MI_COOP_VOC1: case MI_COOP_VOC2:\n"
                                "    case MI_COOP_VOC3: case MI_COOP_VOC4: case MI_COOP_VOC5:\n"
                                "        coop_start_vocation_action(id); break;\n"
                                "    case MI_SAVE_EXPORT: save_export(); break;", 1)
    return {
        "runtime/card.c": card,
        "runtime/menu.h": head,
        "runtime/menu_items.c": items,
        "runtime/frontend_sdl.c": frontend,
    }

def install(root):
    paths = ("runtime/card.c", "runtime/menu.h", "runtime/menu_items.c",
             "runtime/frontend_sdl.c")
    existing = {}
    for name in paths:
        path = root / name
        if not path.is_file():
            raise ValueError(f"Expected DQIX Enhanced source missing: {path}")
        existing[name] = path.read_text(encoding="utf-8")
    modified = changes(existing)
    if not modified:
        return "DQIX-Coop menu already installed"
    for name in paths:
        backup = root / (name + ".dqix-coop-menu-backup")
        if backup.exists():
            raise ValueError(f"Backup exists, but menu is not installed: {backup}")
    # Prepare every output before writing anything.
    for name, new in modified.items():
        if new == existing[name]:
            raise ValueError(f"Source did not change: {name}")
    try:
        for name in paths:
            (root / (name + ".dqix-coop-menu-backup")).write_text(
                existing[name], encoding="utf-8")
        for name, new in modified.items():
            (root / name).write_text(new, encoding="utf-8")
    except OSError:
        for name, original in existing.items():
            (root / name).write_text(original, encoding="utf-8")
        raise
    return "Installed six-option native menu (Game > Starting vocation)"

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, help="Separate DQIX Enhanced SOURCE directory")
    a = p.parse_args(argv)
    try:
        print(install(a.source))
        return 0
    except (OSError, ValueError) as error:
        p.exit(1, f"Error: {error}\n")

if __name__ == "__main__":
    sys.exit(main())
