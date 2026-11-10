# Test the integrated starting-vocation menu (Windows)

This is an **experimental native game build**, not the previous Python save selector. It adds a six-choice menu inside the modified DQIX Enhanced PC game.

## Build a separate test version

1. Download this feature branch as ZIP from the GitHub **Code** menu, then extract it.
2. Double-click **Build DQIX Coop Playtest.bat**.
3. Choose a `.nds` ROM dumped from your own DQIX cartridge.
4. Choose a parent folder (e.g. Desktop) for the new `DQIX-Coop-Playtest` directory.
5. The builder downloads the pinned DQIX Enhanced source, installs the original C mod and menu, then launches the upstream Windows build process. Wait until it finishes and tells you where it put the test game.

Your original DQIX Enhanced install and existing save are not replaced. The new playtest may compile for the first time, depending on MSYS2 availability.

## Use the in-game menu

1. Find `DQIX-Coop-Playtest/game` and make sure `dqix.exe` exists.
2. Copy a **disposable**, normal, early level-1 **Minstrel** save there as `dqix.sav` (not an already-modified Mage or Warrior save). Preserve the original save elsewhere.
3. Launch `game/dqix.exe` or upstream's launch shortcut (if it needs a companion launcher, use upstream's `game/play.bat`).
4. Open **Game > Starting vocation (fresh saves only)** (also shown in the controller in-game menu).
5. Choose **Warrior, Martial Artist, Mage, Priest, Thief, or Minstrel**.
6. Confirm; the game backs up the test save, writes the selected vocation, and restarts automatically.
7. Inspect vocation/attributes/spells and save/reload persistence. If it refuses the save, use the original early Minstrel baseline, not the progressed Mage test save.

### Limitations

This menu is **in the modified game's Game menu**, not inside the original DS character-creation panel. The original Guardian prologue is preserved; a vocation can be changed at the first eligible Level 1 Minstrel save. Moving the selection directly into the original avatar-creation sequence requires further game-code reverse engineering.

The code passed automated C syntax checks against a pinned DQIX Enhanced source revision, plus synthetic-save C tests and Python tests. A full build/run on a privately provided ROM has not been tested. No ROM or game binary is distributed.
