"""Tests with synthetic saves only; no copyrighted game data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

p = Path(__file__).resolve().parents[1] / 'tools' / 'set_starting_vocation.py'
spec = importlib.util.spec_from_file_location('set_starting_vocation', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_save(exp=7, standby=3):
    data = bytearray(65536)
    data[:len(mod.MAGIC)] = mod.MAGIC
    for slot in (0, 1):
        b = bytearray(data[slot * mod.SLOT_SIZE:(slot + 1) * mod.SLOT_SIZE])
        b[mod.SAVE_EXISTS] = 1
        b[mod.STANDBY_COUNT] = standby
        b[mod.PARTY_COUNT] = 1
        h = mod.CHARACTER_OFFSET + mod.CHARACTER_SIZE * standby
        b[h + mod.CURRENT_VOCATION] = 6
        for v in range(1, 7):
            b[h + mod.LEVELS + v] = 1
        b[h + mod.EXPS + 6 * 4:h + mod.EXPS + 7 * 4] = exp.to_bytes(4, 'little')
        mod.rewrite_checksums(b)
        data[slot * mod.SLOT_SIZE:(slot + 1) * mod.SLOT_SIZE] = b
    return bytes(data)


class TestSavePatch(unittest.TestCase):
    def test_each_starting_vocation_and_both_slots(self):
        original = fake_save()
        for name, idx in mod.VOCATIONS.items():
            if idx == 6:
                continue
            altered = mod.patch_save(original, name)
            for slot in (0, 1):
                start = slot * mod.SLOT_SIZE
                local_hero = mod.CHARACTER_OFFSET + 3 * mod.CHARACTER_SIZE
                self.assertEqual(altered[start + local_hero + mod.CURRENT_VOCATION], idx)
                self.assertTrue(mod.checksums_ok(altered[start:start + mod.SLOT_SIZE]))
                expected_changes = set(range(start + 132, start + 136))
                expected_changes.add(start + local_hero + mod.CURRENT_VOCATION)
                observed_changes = {i for i in range(start, start + mod.SLOT_SIZE)
                                    if altered[i] != original[i]}
                self.assertTrue(observed_changes <= expected_changes)
                self.assertEqual(int.from_bytes(altered[start + local_hero + mod.EXPS + 24:
                                                        start + local_hero + mod.EXPS + 28], 'little'), 7)

    def test_blank_initialized_slots_have_clear_error(self):
        blank = bytearray(fake_save())
        for slot in (0, 1):
            base = slot * mod.SLOT_SIZE
            blank[base + mod.SAVE_EXISTS] = 0
            blank[base + mod.STANDBY_COUNT] = 255
            blank[base + mod.PARTY_COUNT] = 255
            # Blank slots commonly do not have all valid CRCs.
            blank[base + 36:base + 40] = b'\\x00' * 4
        with self.assertRaisesRegex(mod.SaveError, 'contains no started character'):
            mod.patch_save(bytes(blank), 'mage')

    def test_occupied_corrupt_slot_still_rejected(self):
        broken = bytearray(fake_save())
        broken[mod.CHARACTER_OFFSET + 18] ^= 1
        with self.assertRaisesRegex(mod.SaveError, 'invalid checksums in an occupied slot'):
            mod.patch_save(bytes(broken), 'mage')

    def test_zero_exp_still_supported(self):
        self.assertEqual(mod.patch_save(fake_save(exp=0), 'mage')[1932], 3)

    def test_invalid_input(self):
        with self.assertRaises(mod.SaveError):
            mod.patch_save(b'anything', 'mage')
        broken = bytearray(fake_save())
        broken[250] ^= 8
        with self.assertRaisesRegex(mod.SaveError, 'checksums'):
            mod.patch_save(broken, 'mage')

    def test_reject_progressed(self):
        original = bytearray(fake_save())
        b = original[:mod.SLOT_SIZE]
        h = mod.CHARACTER_OFFSET + mod.CHARACTER_SIZE * 3
        b[h + mod.LEVELS + 6] = 2
        mod.rewrite_checksums(b)
        original[:mod.SLOT_SIZE] = b
        with self.assertRaisesRegex(mod.SaveError, 'level-1'):
            mod.patch_save(original, 'mage')

    def test_reject_mismatch_second_slot(self):
        original = bytearray(fake_save())
        second = bytearray(original[mod.SLOT_SIZE:])
        h = mod.CHARACTER_OFFSET + mod.CHARACTER_SIZE * 3
        second[h + mod.CURRENT_VOCATION] = 1
        mod.rewrite_checksums(second)
        original[mod.SLOT_SIZE:] = second
        with self.assertRaisesRegex(mod.SaveError, 'Expected Minstrel'):
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
