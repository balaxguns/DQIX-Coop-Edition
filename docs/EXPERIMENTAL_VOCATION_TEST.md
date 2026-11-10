# Experimental vocation-save test

**Current status: real save data structurally validated; in-game behavior not yet verified.** This is a temporary save-file prototype, not the requested six-choice in-game character-creation UI.

## Confirmed first usable save

The first ordinary save after the mandatory opening battle can have a level-1 Minstrel with **7 EXP**. The prototype now allows exactly 0 or 7 EXP at level 1, rather than incorrectly requiring a 0-EXP character. Five separate trial saves were generated from such a save and checked: the sole data changes in each of the two save slots are the current-vocation byte and the checksum covering it.

One publicly available save-layout reference is [DQIX/editor](https://github.com/DQIX/editor), which documents the 65,536-byte save format, its two 32,768-byte slots, the vocation byte, separate per-vocation EXP and level fields, and three CRC32 regions per slot.

## Behavior and limitations

- Selected vocation IDs: Warrior 1, Priest 2, Mage 3, Martial Artist 4, Thief 5. Minstrel 6 is the original baseline.
- Keeps the mandatory battle's 7 EXP assigned to Minstrel, leaves the selected target vocation at level 1 with 0 EXP, and leaves advanced-class unlock flags alone.
- Rewrites checksums in **both** save slots because DQIX retains two copies of save-state data.
- Requires both slots to have usable, untouched level-1 Minstrel character records; does not work on blank new game files or progressed saves.
- The patcher refuses overwriting input and existing output; do not place modified saves in your ordinary game installation until you have made a complete backup.
- **Unknown:** will the game recompute HP/MP, character stats, initial equipment permissions, spells, and battle formulas correctly on load? These require an actual game test.

## Generate a test save (developer use)

```powershell
py -3 tools/set_starting_vocation.py "C:\\dqix-test\\dqix.sav" warrior
```

The output is `dqix-warrior.sav`, distinct from the original `dqix.sav`. For testing in an **isolated** game directory, rename the output to `dqix.sav` only after saving the baseline original separately.

## How to validate

1. Make an isolated copy of the playable game folder, including `dqix.exe` and any required game files. Do not upload or publish it.
2. Back up the isolated copy's `dqix.sav` as an offline, safe copy.
3. Replace **only** that isolated copy's `dqix.sav` with one generated test save, renamed `dqix.sav`.
4. Start the isolated game; inspect vocation, character details, equipment screen, available spells, and whether battle works.
5. Save, close, reopen and confirm the new vocation persists. If this fails, restore your backup and record what happened.
6. Repeat with other vocation variants only after one succeeds.

**Never distribute ROMs, extracted game files, or the packaged game executable.**

Automated synthetic-save tests are in `tests/test_starting_vocation.py`. In-game tests have not yet been run.
