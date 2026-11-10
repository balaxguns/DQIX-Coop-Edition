# Native vocation proof of concept (experimental)

This branch introduces **actual C code integrated into DQIX Enhanced's save-chip startup path**. This is a step beyond the Python save editor, but **not** the final character-creation menu and **not yet verified on Windows**.

## What it does

When an explicitly configured test build loads an existing, eligible level-1 Minstrel save, it changes the current vocation to Warrior, Priest, Mage, Martial Artist, or Thief **before the game reads the save data**. It then lets DQIX handle the selected vocation's stats, spells and gameplay. The only modified save bytes are the selected vocation and slot checksums. The already-earned 7 Minstrel EXP remains with Minstrel.

This prototype is designed to test whether runtime save initialization is a viable mod hook; it does **not** present a choice during the original character-creation scene and does not bypass the initial Guardian storyline.

## Safeguards

- The native hook is inert unless `DQIX_START_VOCATION` is explicitly set.
- It requires **both save slots** to have valid checksums, an existing hero, and untouched Level-1 Minstrel state (0 or 7 EXP). It rejects progressed or mixed saves.
- Any rejection leaves the save image unchanged. The hook validates **both slots before writing either**.
- No advanced-vocation flags, story flags, equipment, or experience are changed.
- Test only in an **isolated copy** of the DQIX Enhanced game directory. The modified test build may persist changes to the test copy's save on normal exit; never point it at the only copy of your save.
- No ROM, game binary, or copyrighted resources are committed.

## Developer workflow

1. Work from a separately downloaded **source** checkout of [DQIX Enhanced](https://github.com/sackchief/dqix-enhanced) compatible with `runtime/card.c`. Keep the base game and existing saves untouched.
2. In a cloned `DQIX-Coop-Edition` folder, run:

   ```powershell
   py -3 tools/install_native_hook.py "C:\\path\\to\\dqix-enhanced-source"
   ```

   The installer backs up upstream `runtime/card.c` to `runtime/card.c.dqix-coop-backup`, adds `runtime/dqix_vocation.c`, and inserts the hook before the save is initialized. It is idempotent and refuses unknown upstream source structures.

3. Build your **test copy** through upstream's documented `BUILD.bat` using **your own** ROM, kept outside this repository. Build dependencies, gameplay, and linking remain untested in this branch.
4. In a disposable test installation, with the early Minstrel save backed up, set a vocation before launch using a temporary command prompt:

   ```bat
   set DQIX_START_VOCATION=mage
   game\\play.bat
   ```

   **Warning:** `game\\play.bat` may not exist in every upstream version. Launch from the patched source directory using the generated launcher appropriate for that version. The environment setting applies to that launch only; don't set it globally.

5. Watch the console log for `[DQIX-Coop]` either confirming the selection or refusing an ineligible save. Only inspect the isolated test save.

## Testability without game material

The repository contains:
- `native/dqix_vocation.c`: independently written C implementation.
- `tests/test_native_vocation.c`: self-contained C tests against synthetic save images (correct IDs, CRCs, atomic rejection).
- `tools/install_native_hook.py`: installer that only edits a source checkout.
- `tests/test_install_native_hook.py`: source-injection tests in a fake upstream tree.
- GitHub Actions native compilation and Python test jobs.

To run tests on Linux with GCC:

```sh
cc -std=c11 -Wall -Wextra -Werror -pedantic tests/test_native_vocation.c -o /tmp/dqix-vocation-test
/tmp/dqix-vocation-test
python -m unittest discover -s tests -v
```

## Known gaps

The runtime patch does not give the user a vocation choice *during character creation*, only at save load on explicit opt-in. Actual in-game selection requires discovery of the Guardian-to-Minstrel transition and a new native UI or game script integration. Multiplayer synchronization, full progression, equipment restrictions, and compatibility with current upstream builds remain unverified.

Do not merge this branch as a finished game mod or tell users that the complete requested feature works.

## Integrated six-choice Game menu (branch update)

The opt-in runtime hook above has now been extended to the **actual DQIX Enhanced Game menu**, shared by the Windows menu bar and its SDL controller/keyboard menu:

- `Game > Starting vocation (fresh saves only)`
- Warrior / Martial Artist / Mage / Priest / Thief / Minstrel (original)
- Confirm a selection; make a separate dated save backup; change both valid early Minstrel save slots and their checksums; restart to load the selected vocation.
- If the save is not eligible, no vocation bytes change and an error explains why.
- Multiplayer sessions are refused to prevent divergence.
- The Guardian/Celestial opening and advanced vocation unlocks are untouched.

**Important scope distinction:** This menu is part of DQIX Enhanced's game menu, **not the original DS character-creation UI**. The selection becomes available on the first eligible saved Level 1 Minstrel, after the Guardian storyline. Completing a selection on the original character-creation screen remains separate future reverse-engineering work. The user's successful standalone selector and Mage playtest support the save format, but do not prove this native menu's gameplay behavior.

### Easier Windows test-build preparation

A separate test installation can be prepared with [Build DQIX Coop Playtest.bat](../Build%20DQIX%20Coop%20Playtest.bat). It prompts for a personally dumped `.nds`, downloads the **pinned source only** from DQIX Enhanced, applies both local code installers, and invokes upstream's `BUILD.bat` to compile a new test game into a chosen parent directory's `DQIX-Coop-Playtest` folder.

It does **not** modify the currently installed copy. If the test folder already exists, it refuses to overwrite it. The build still needs to run on Windows using a local ROM and a working network/toolchain; we cannot verify it launches without such a local test. Use an **early unmodified Minstrel save**, not the Mage or Warrior test save, when playtesting the new menu. Preserve the original elsewhere.

CI now checks native C compilation, synthetic-save tests, Python tests, and the patched DQIX Enhanced source **C syntax** without accessing any ROM. A passing syntax check does not prove the full Windows link or runtime behavior.
