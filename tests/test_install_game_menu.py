"""Tests game-menu source integration without ROMs or proprietary assets."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

P = Path(__file__).resolve().parents[1] / "tools" / "install_game_menu.py"
spec = importlib.util.spec_from_file_location("install_game_menu", P)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MenuTests(unittest.TestCase):
    def base(self):
        return {
            "runtime/card.c": """
#include <stdint.h>
#include <stdlib.h>
static unsigned char g_backup[65536];
static size_t g_backup_size;
static int g_backup_dirty;
void backup_flush(void) {}
int dqix_apply_start_vocation(unsigned char* p, size_t n, const char* v);
const char* backup_path(void) { return g_backup_path; }
""",
            "runtime/menu.h": """
enum {
    MI_DISCORD = 340,
};
""",
            "runtime/menu_items.c": """
        SUB("Save &file"),
            IT(MI_SAVE_EXPORT, "Export", NULL),
        END,
""",
            "runtime/frontend_sdl.c": """
static void save_backup_copy(char* out, size_t n) { out[0] = 0; }
void frontend_frame(void) { }
static void do_action(int id) {
    switch (id) {
    case MI_SAVE_EXPORT: save_export(); break;
    }
}
""",
        }

    def test_injects_six_options_into_runtime(self):
        changed = module.changes(self.base())
        self.assertEqual(set(changed), set(self.base()))
        for k in ("MI_COOP_VOC0", "MI_COOP_VOC1", "MI_COOP_VOC2",
                  "MI_COOP_VOC3", "MI_COOP_VOC4", "MI_COOP_VOC5"):
            self.assertIn(k, changed["runtime/menu_items.c"])
        self.assertIn("coop_start_vocation_action(id)", changed["runtime/frontend_sdl.c"])
        self.assertIn("coop_vocation_prompt_once();", changed["runtime/frontend_sdl.c"])
        self.assertIn("Choose starting vocation", changed["runtime/frontend_sdl.c"])
        self.assertIn("dqix_coop_start_vocation_eligible", changed["runtime/card.c"])
        self.assertIn("save_backup_copy(kept", changed["runtime/frontend_sdl.c"])
        self.assertIn("restart_with(NULL)", changed["runtime/frontend_sdl.c"])
        self.assertIn("dqix_apply_start_vocation(g_backup", changed["runtime/card.c"])

    def test_install_repeat_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            originals = self.base()
            for path, text in originals.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            self.assertIn("Installed", module.install(root))
            self.assertIn("already installed", module.install(root))
            for path, text in originals.items():
                backup = root / (path + ".dqix-coop-menu-backup")
                self.assertEqual(backup.read_text(encoding="utf-8"), text)
                self.assertNotEqual((root / path).read_text(encoding="utf-8"), text)

    def test_drift_refused_with_no_changes(self):
        original = self.base()
        original["runtime/menu_items.c"] = "unexpected"
        with self.assertRaisesRegex(ValueError, "menu_items.c changed"):
            module.changes(original)


if __name__ == "__main__":
    unittest.main()
