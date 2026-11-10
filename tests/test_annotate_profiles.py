"""Pure Python tests for profile-to-symbol annotation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "annotate_profiles.py"
spec = importlib.util.spec_from_file_location("annotate_profiles", path)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

class AnnotationTests(unittest.TestCase):
    def test_unique_and_ambiguous_overlay_addresses(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root = base / "config"
            root.mkdir()
            (root / "symbols.txt").write_text("Player kind:function(arm,size=0x10) addr:0x02001234\n")
            for overlay in ("ov000", "ov001"):
                sub = root / "overlays" / overlay
                sub.mkdir(parents=True)
                (sub / "symbols.txt").write_text(f"func_{overlay} kind:function(arm,size=0x10) addr:0x021536e0\n")
            p = base / "profile.txt"
            p.write_text(" 3 ARM9 02001234 Player\n 7 ARM9 021536e0 ?\n 2 ARM7 021536e0 excluded\n")
            result = tool.annotate(p, tool.load_symbols(root))
            self.assertEqual(len(result), 2)
            self.assertTrue(result[0][2].startswith("AMBIGUOUS "))
            self.assertEqual(result[1][2], "main:Player")

    def test_missing_symbols(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                tool.load_symbols(Path(d))
if __name__ == "__main__":
    unittest.main()
