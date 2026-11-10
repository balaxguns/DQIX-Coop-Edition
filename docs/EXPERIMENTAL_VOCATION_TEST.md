# Experimental starting-vocation save prototype

**Not yet the requested creation-screen mod.** This prototype edits a **copy** of an unprogressed, fresh DQIX Enhanced save so that the protagonist's current vocation is one of Warrior, Priest, Mage, Martial Artist, or Thief, instead of Minstrel.

## Verified against public save format

The community [DQIX editor](https://github.com/DQIX/editor) identifies:
- two 32,768-byte slots in a 65,536-byte DQIX `.sav` file;
- hero character array, vocation field, per-vocation level and experience;
- CRC32 checksums for each save slot;
- vocation IDs 1–6 for standard classes;
- advanced vocation unlock flags at another save offset.

The script intentionally only edits the hero's current vocation byte and recalculates the owning slot's checksum. It does not modify quest flags, unlock flags, equipment, or stats. Those are precisely the parts that need **in-game verification** to see whether DQIX recalculates dependent data when loading a save.

## Safety

- Never writes over the input file or an existing output.
- Requires an existing file with exact size, magic header, and valid checksums.
- Requires an existing player character with current vocation Minstrel, at level 1, with 0 XP.
- Requires the target vocation to be level 1 with 0 XP.
- Does not try to change a Guardian, advanced vocation, or progressed hero.
- Never uploads your save to GitHub.
- This is a proof-of-concept for test saves, **not** a multiplayer-ready patch.

## Command example

From the root of this repository on a Windows computer with Python 3:

```powershell
py -3 tools/set_starting_vocation.py "C:\\testing\\dqix.sav" mage
```

This creates `C:\testing\dqix-mage.sav` without changing `dqix.sav`. Never point it at a save you haven't backed up.

The script defaults to normal save slot 0. Experimental `--slot 1` is possible for a quick-save slot, but only use when you know exactly which slot is active.

Tests (no game copy required):

```powershell
py -3 -m unittest discover -s tests -p "test_starting_vocation.py" -v
```

The Python unit tests were executed locally against **synthetic saves** (four tests passing). This does **not** establish correctness on a real game save.

## Real-game acceptance test, pending

1. Create a disposable brand-new hero in an isolated DQIX Enhanced game folder.
2. Advance until the normal save is actually available, without leveling up.
3. Back up its `dqix.sav`. Do not replace your regular save.
4. Apply the tool to a **copy**, then load the resulting file in that isolated game folder.
5. Check displayed class, HP/MP, spell/skill progression, equipment restrictions, level-ups, and whether the save reloads.
6. Never share your personal ROM, copied game files, or private full save through GitHub.

The requested in-game creation menu and verified class stat initialization remain future implementation tasks; changing a save afterward is not equivalent to completing those features.
