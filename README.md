# DQIX-Coop-Edition

A community modification project for **Dragon Quest IX: Sentinels of the Starry Skies**, focused on six selectable starting vocations and compatibility with online multiplayer.

> **Status: research and scaffolding.** No playable mod, vocation-selection patch, installer, or multiplayer modification has been implemented or tested in this repository yet.

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

## Read the project documents

- [Project requirements](docs/PROJECT_SCOPE.md)
- [Technical implementation plan](docs/TECHNICAL_PLAN.md)
- [Beginner setup](docs/GETTING_STARTED.md)
- [Manual test matrix](docs/TEST_MATRIX.md)

## Upstream and game files

Potential foundation: [DQIX Enhanced](https://github.com/sackchief/dqix-enhanced), which requires each user to provide their own cartridge ROM to build a native PC version. Its source is licensed GPL-3.0-or-later. Before incorporating any upstream source, we will preserve required licenses and notices.

**Do not upload** a DQIX ROM, extracted proprietary data, saves containing personal data, generated Windows game executable, or assets copied from the commercial game. This repository distributes research, independently written patch source, and building instructions only.

Not affiliated with or endorsed by Square Enix, Nintendo, or the upstream project.
