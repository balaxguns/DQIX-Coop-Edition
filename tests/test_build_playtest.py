"""Builder tests — synthetic archives only, no ROM or downloads."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

p = Path(__file__).resolve().parents[1] / "tools" / "build_playtest.py"
spec = importlib.util.spec_from_file_location("build_playtest", p)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def fake_zip(name="dqix-enhanced-source/BUILD.bat"):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as archive:
        archive.writestr(name, "@echo off\n")
        archive.writestr("dqix-enhanced-source/runtime/card.c", "test\n")
    return data.getvalue()


class BuilderTests(unittest.TestCase):
    def test_extract_preserves_structure(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "playtest"
            builder.extract_verified_zip(fake_zip(), target)
            self.assertTrue((target / "BUILD.bat").is_file())
            self.assertTrue((target / "runtime" / "card.c").is_file())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "playtest"
            target.mkdir()
            with self.assertRaises(FileExistsError):
                builder.extract_verified_zip(fake_zip(), target)

    def test_rejects_archive_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            bad = fake_zip("../payload")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                builder.extract_verified_zip(bad, Path(d) / "playtest")
            self.assertFalse((Path(d) / "payload").exists())


if __name__ == "__main__":
    unittest.main()
