# DQIX-Coop-Edition

A community modification project for **Dragon Quest IX: Sentinels of the Starry Skies**, focused on six selectable starting vocations and compatibility with online multiplayer.

> **Status: experimental prototype.** A standalone save-file vocation selector has been implemented, and a Mage save has been tested in the game with appropriate-looking stats, Frizz, and Frizz persistence after reload. **The requested in-game character-creation screen has not been implemented.** No new multiplayer logic has been implemented.

## What we want to change

At initial character creation, select exactly one of:
- Warrior
- Martial Artist
- Mage
- Priest
- Thief
- Minstrel

The character should begin at **level 1** using the original game's accurate vocation-specific state. Preserve custom appearance, equipment restrictions, skill/spell progression and original gameplay. Advanced vocations remain quest-locked; later vocation changes continue at Alltrades Abbey.

## Playing online

The upstream [DQIX Enhanced](https://github.com/sackchief/dqix-enhanced) project documents original-style co-op over the internet for up to four players. This does **not** automatically provide coordinated campaign story progression or co-op at the beginning of a brand-new save. We'll treat testing remote multiplayer and changing campaign gates as distinct tasks.

## Usable experimental tools

- [Windows-friendly vocation selector (Python/Tkinter)](tools/vocation_selector_gui.py) — creates a **separate** test save from a suitable early-game save and never replaces the original automatically. The code is a local utility, not part of the game UI.
- [Safe command-line save patcher](tools/set_starting_vocation.py) — underlying prototype; only supports specific early Minstrel saves.
- [Synthetic-save unit tests](tests/test_starting_vocation.py) and [CI workflow](.github/workflows/python-tests.yml).
- [Experimental save test details](docs/EXPERIMENTAL_VOCATION_TEST.md).

## Read the project documents

- [Project requirements](docs/PROJECT_SCOPE.md)
- [Technical implementation plan](docs/TECHNICAL_PLAN.md)
- [Beginner setup](docs/GETTING_STARTED.md)
- [Manual test matrix](docs/TEST_MATRIX.md)

## Upstream and game files

Potential foundation: [DQIX Enhanced](https://github.com/sackchief/dqix-enhanced), which requires each user to provide their own cartridge ROM to build a native PC version. Its source is licensed GPL-3.0-or-later. Before incorporating any upstream source, we will preserve required licenses and notices.

**Do not upload** a DQIX ROM, extracted proprietary data, saves containing personal data, generated Windows game executable, or assets copied from the commercial game. This repository distributes research, independently written patch source, and building instructions only.

Not affiliated with or endorsed by Square Enix, Nintendo, or the upstream project.
