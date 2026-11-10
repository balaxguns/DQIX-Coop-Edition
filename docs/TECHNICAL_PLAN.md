# Technical plan and evidence checkpoints

## Foundation candidates
- [DQIX Enhanced](https://github.com/sackchief/dqix-enhanced): native Windows rebuild from each player's own cartridge-derived ROM; documents internet multiplayer via the game's original host/guest visit features. It does **not** automatically mean co-op campaign from a fresh save.
- [DQIX decomp](https://github.com/DQIX/dqix-decomp): decompilation/research source for understanding the original game. Work remains in progress.
- [DQIX Editor](https://github.com/dqix/editor): save-editor research reference; not a replacement for a creation-screen patch.

Do not vendor third-party source without checking its license, attribution requirements and project structure. DQIX Enhanced describes GPL-3.0-or-later licensing; any derivative source distribution must comply with that license.

## Investigation sequence
1. Clone DQIX Enhanced locally and read its README, technical documentation, build instructions and license; record the exact upstream commit.
2. Build the **unmodified** upstream using a personally dumped, region-matched ROM. Keep it outside this repository.
3. Identify game functions/data for player creation, protagonist initialization, initial vocation assignment, and vocation stat initialization, using debug symbols or decompilation mapping.
4. Identify the correct creation UI change; avoid setting only the displayed vocation while leaving internal progression as Minstrel.
5. Write a design mapping each of the six starting options to verified game IDs; do not guess numeric IDs.
6. Implement a minimal, reversible patch on a feature branch. Prefer using the original game's vocation initialization code path.
7. Test six fresh saves, later level-ups, equipment, save/load, transitions, and progression to Alltrades Abbey.
8. Verify multiplayer interoperability with same-version builds; distinguish network connection from story/quest synchronization.
9. Provide patch source and instructions for each owner to build from their own game copy. Never commit proprietary assets/ROMs/generated game binaries.

## Milestone 1 deliverable
A confirmed upstream revision, documented build steps, verified creation/vocation function references and an implementation PR with real code and repeatable test results.

## Milestone 2 deliverable
Validated six-vocation character creation using a fresh save on Windows.

## Milestone 3 deliverable
Test original remote guest multiplayer with the patched version, document known story-gating limits, and decide if fresh-save co-op requires a separately scoped engine-level feature.

## Current status
Repository scaffolding only. No patch implemented; no build or runtime verification has been performed.
