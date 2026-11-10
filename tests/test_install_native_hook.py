"""Exercise source injection with a minimal fake upstream tree; no ROM needed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "install_native_hook.py"
spec = importlib.util.spec_from_file_location("install_native_hook", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class InstallerTests(unittest.TestCase):
    def upstream(self, root):
        runtime = root / "runtime"
        runtime.mkdir()
        card = runtime / "card.c"
        # Mimics only the required structure of upstream's backup_init.
        card.write_text(
            '#include <stdlib.h>\n#include <stdio.h>\n'
            'static char* g_backup_at_boot;\nstatic size_t g_backup_size;\n'
            'static int g_backup_dirty;\nstatic unsigned char g_backup[65536];\n'
            'void backup_init(const char* path) {\n'
            '    if (path) { int x = 1; (void)x; }\n'
            '    g_backup_at_boot = malloc(g_backup_size);\n'
            '}\n', encoding="utf-8")
        return card

    def test_install_once_and_twice(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            card = self.upstream(root)
            before = card.read_bytes()
            source = root / "addon.c"
            source.write_text("int original_addon;\n", encoding="utf-8")
            result = mod.install(root, source)
            self.assertIn("Installed", result)
            text = card.read_text(encoding="utf-8")
            self.assertIn(mod.HOOK, text)
            self.assertIn(mod.PROTOTYPE, text)
            self.assertEqual((root / "runtime" / "dqix_vocation.c").read_bytes(), source.read_bytes())
            self.assertEqual((root / "runtime" / "card.c.dqix-coop-backup").read_bytes(), before)
            self.assertIn("Already installed", mod.install(root, source))
            self.assertEqual(card.read_text(encoding="utf-8"), text)

    def test_unknown_upstream_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.joinpath("runtime").mkdir()
            card = root / "runtime" / "card.c"
            card.write_text("unrecognized source")
            source = root / "addon.c"
            source.write_text("int original_addon;")
            with self.assertRaisesRegex(ValueError, "Unexpected upstream"):
                mod.install(root, source)
            self.assertEqual(card.read_text(), "unrecognized source")
            self.assertFalse((root / "runtime" / "dqix_vocation.c").exists())


if __name__ == "__main__":
    unittest.main()
