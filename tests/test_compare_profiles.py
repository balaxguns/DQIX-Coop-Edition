"""Unit tests for profile ranking. No game ROM or build required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "compare_profiles.py"
spec = importlib.util.spec_from_file_location("compare_profiles", FILE)
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)

class ProfileTests(unittest.TestCase):
    def test_rank(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.txt", Path(directory) / "b.txt"
            a.write_text("  4 ARM9 02001234 common\n  8 ARM7 02009000 other\n")
            b.write_text(" 10 ARM9 02001234 common\n  2 ARM9 0200abcd new\n 15 ARM7 02009000 other\n")
            rows = profile.compare(profile.parse_profile(a), profile.parse_profile(b))
            self.assertEqual([(r[0], r[4]) for r in rows], [(6, "02001234"), (2, "0200abcd")])
            self.assertEqual(len(profile.compare(profile.parse_profile(a), profile.parse_profile(b), arm9_only=False)), 3)

    def test_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "empty.txt"
            p.write_text("nothing")
            with self.assertRaises(ValueError):
                profile.parse_profile(p)

    def test_accumulates(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "repeat.txt"
            p.write_text(" 2 ARM9 02001234 a\n 5 ARM9 02001234 a\n")
            self.assertEqual(profile.parse_profile(p)[("9", "02001234")][0], 7)

if __name__ == "__main__":
    unittest.main()
