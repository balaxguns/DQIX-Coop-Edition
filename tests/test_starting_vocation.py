"""Tests with synthetic saves only; no copyrighted game data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

p = Path(__file__).resolve().parents[1] / 'tools' / 'set_starting_vocation.py'
spec = importlib.util.spec_from_file_location('set_starting_vocation', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_save():
    data = bytearray(65536)
    data[:len(mod.MAGIC)] = mod.MAGIC
    for slot in (0, 1):
        b = bytearray(data[slot * mod.SLOT_SIZE:(slot + 1) * mod.SLOT_SIZE])
        b[mod.SAVE_EXISTS] = 1
        b[mod.PARTY_COUNT] = 1
        h = mod.CHARACTER_OFFSET
        b[h + mod.CURRENT_VOCATION] = 6
        for v in range(1, 7):
            b[h + mod.LEVELS + v] = 1
        mod.rewrite_checksums(b)
        data[slot * mod.SLOT_SIZE:(slot + 1) * mod.SLOT_SIZE] = b
    return bytes(data)


class TestSavePatch(unittest.TestCase):
    def test_each_starting_vocation(self):
        original = fake_save()
        for name, idx in mod.VOCATIONS.items():
            if idx == 6:
                continue
            altered = mod.patch_save(original, name)
            self.assertEqual(altered[mod.CHARACTER_OFFSET + mod.CURRENT_VOCATION], idx)
            self.assertEqual(original[mod.SLOT_SIZE:], altered[mod.SLOT_SIZE:])
            self.assertEqual(original[:132], altered[:132])
            self.assertTrue(mod.checksums_ok(altered[:mod.SLOT_SIZE]))
            diffs = {i for i, (a, b) in enumerate(zip(original, altered)) if a != b}
            self.assertTrue(diffs <= set(range(132, 136)) | {216})

    def test_invalid_input(self):
        with self.assertRaises(mod.SaveError):
            mod.patch_save(b'anything', 'mage')
        broken = bytearray(fake_save())
        broken[250] ^= 8
        with self.assertRaisesRegex(mod.SaveError, 'checksums'):
            mod.patch_save(broken, 'mage')

    def test_not_fresh(self):
        original = bytearray(fake_save())
        original[mod.CHARACTER_OFFSET + mod.LEVELS + 6] = 2
        b = original[:mod.SLOT_SIZE]
        mod.rewrite_checksums(b)
        original[:mod.SLOT_SIZE] = b
        with self.assertRaisesRegex(mod.SaveError, 'progressed'):
            mod.patch_save(original, 'mage')

    def test_no_accidental_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'save.sav'
            path.write_bytes(fake_save())
            self.assertEqual(mod.main([str(path), 'priest']), 0)
            self.assertEqual(path.read_bytes(), fake_save())
            created = path.with_name('save-priest.sav')
            self.assertTrue(created.is_file())
            with self.assertRaises(SystemExit):
                mod.main([str(path), 'priest'])


if __name__ == '__main__':
    unittest.main()
