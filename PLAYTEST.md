# DQIX-Coop: character-creation vocation playtest (Windows)

This build adds a **new-game vocation choice** to the PC game, not merely an option to edit an existing save.

## Where it appears

With a **blank, new-game save**, the game displays **Create your hero: starting vocation**, offering Warrior, Martial Artist, Mage, Priest, Thief, and Minstrel. It appears before the usual DS title and character-appearance creation sequence, rather than inside the original DS character editor.

Your choice remains pending while you play the mandatory Celestrian/Guardian prologue. When the game saves an eligible Level 1 Minstrel adventurer (the confirmed prototype supports 0 or 7 EXP with valid matching slots), the runtime applies the chosen class, saves, and restarts to load that vocation's attributes and spells. A save that does not match is left unchanged, and the choice remains pending. Minstrel keeps the original behavior.

The precise story point when the original game first writes this eligible save **is not yet verified**; actual game testing is needed to establish that the change persists across the transition.

## Build a completely separate copy

1. Open the [feature branch](https://github.com/balaxguns/DQIX-Coop-Edition/tree/feature/native-starting-vocation) and use **Code > Download ZIP**.
2. Extract the project and double-click **Build DQIX Coop Playtest.bat**.
3. Choose a personal DQIX .nds cartridge dump and a parent folder for the new test game.
4. The builder prepares source, installs the new creation-stage and save-chip code, then runs the original DQIX Enhanced BUILD.bat.
5. The built game should appear at DQIX-Coop-Playtest/game/dqix.exe.

The builder never overwrites a pre-existing DQIX-Coop-Playtest folder. If you previously built a test copy, select a **different parent folder** for the new build. Do not delete or overwrite your existing working game or original saves.

## What to test

1. Launch the new test executable with **no dqix.sav in its game directory**. Back up any test saves before moving them.
2. Confirm the **Create your hero: starting vocation** menu appears before character creation. Select Mage for the first attempt.
3. Use the ordinary appearance editor and Guardian opening. The selected vocation is stored in dqix-coop-start-vocation.txt in the test game's working directory.
4. When the character becomes an adventurer, save normally. The mod should eventually recognize a first Level 1 Minstrel save, apply Mage, and automatically restart.
5. Confirm Mage, Frizz, stats, and saving/reloading. If the choice is applied prematurely during the Guardian prologue, or never applied, report the exact moment.

This version is **not yet a new button inside the original DS appearance editor**. It is an added character-creation stage in the native Windows frontend. Gameplay integration must be verified locally. No ROM, game executable or save is distributed by this project.
