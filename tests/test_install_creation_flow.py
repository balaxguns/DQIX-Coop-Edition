"""Safe tests of creation-flow source installation (no ROM/game assets)."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

module_path = Path(__file__).resolve().parents[1] / "tools" / "install_creation_flow.py"
spec = importlib.util.spec_from_file_location("install_creation_flow", module_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    return {
        "runtime/card.c": """static int g_backup_dirty;
void backup_init(const char* path) { }
void backup_flush(void) {
    if (!g_backup_dirty || !g_backup_path[0]) return;
    FILE* f = fopen(g_backup_path, "wb");
    if (!f) return;
    fwrite(g_backup, 1, g_backup_size, f);
    fclose(f);
    g_backup_dirty = 0;
}
const char* backup_path(void) { return g_backup_path; }
""",
        "runtime/frontend_sdl.c": """void frontend_init(int argc, char** argv) {
    if (g_opt.dlc) backup_unlock_dlc();
}
/* First eligible fresh Minstrel boot: previous prompt */
static void coop_vocation_prompt_once(void) { }
static void do_action(int id) { }
void frontend_frame(void) {
    coop_vocation_prompt_once();
}
"""
    }


class CreationInstallerTests(unittest.TestCase):
    def test_creates_early_selection_and_automatic_application(self):
        out = m.change_source(fixture())
        self.assertIn("coop_creation_tick();", out["runtime/frontend_sdl.c"])
        self.assertNotIn("coop_vocation_prompt_once();", out["runtime/frontend_sdl.c"])
        self.assertIn("Create your hero: starting vocation", out["runtime/frontend_sdl.c"])
        self.assertIn("dqix_coop_creation_set(keys[choice])", out["runtime/frontend_sdl.c"])
        self.assertIn("dqix_coop_creation_blank()", out["runtime/frontend_sdl.c"])
        self.assertIn("dqix_coop_creation_apply_before_flush();", out["runtime/card.c"])
        self.assertIn("dqix_apply_start_vocation(g_backup", out["runtime/card.c"])
        self.assertIn("dqix_coop_creation_boot_complete();", out["runtime/frontend_sdl.c"])
        self.assertIn("dqix-coop-start-vocation.txt", out["runtime/card.c"])

    def test_install_is_idempotent_and_backs_up(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            files = fixture()
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(exist_ok=True, parents=True)
                path.write_text(text, encoding="utf-8")
            self.assertIn("Installed", m.install(root))
            self.assertIn("already installed", m.install(root))
            for name, text in files.items():
                self.assertEqual(
                    (root / (name + ".dqix-coop-creation-backup")).read_text(encoding="utf-8"),
                    text
                )
                self.assertNotEqual((root / name).read_text(encoding="utf-8"), text)

    def test_unknown_source_fails_closed(self):
        files = fixture()
        files["runtime/frontend_sdl.c"] = "unexpected source"
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            m.change_source(files)
        files = fixture()
        files["runtime/card.c"] = "unexpected source"
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            m.change_source(files)


if __name__ == "__main__":
    unittest.main()
