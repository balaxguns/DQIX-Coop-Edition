# Upstream source investigation — 2026-11-10

## Confirmed project base

**Repository:** [sackchief/dqix-enhanced](https://github.com/sackchief/dqix-enhanced)

**Inspected GitHub default-branch snapshot:** `86ff9b1ce6128a52f1e83d110b5c893043df5159` (as surfaced in GitHub code search; pin this commit during implementation).

Confirmed from its README:
- Rebuilds the user's own USA or European NDS cartridge ROM into a native Windows program; does **not** ship game assets.
- Setup scripts: `Install Dragon Quest IX.bat`, `BUILD.bat`.
- Can host remote multiplayer sessions via its Wireless menu, using original Pavo/Erinn interactions; four players max.
- Session users should use the same version.
- Saves live in `game/dqix.sav`.
- Upstream licensed GPL-3.0-or-later.

## Confirmed source layout

The project does **not** contain a conventional complete, readable `src/game` folder.
- `recomp/build.py` and `recomp/insn.py` are part of the recompiler.
- `runtime/` contains PC-facing code, hardware/network/session implementation, rendering and input.
- `config/usa/arm9/symbols.txt`, `config/usa/arm9/relocs.txt`, and `config/usa/arm9/overlays/ovNNN/` contain game-code mapping configuration; many source semantics will require examining the decompilation or tracing original code.
- `tools/build-game.sh` and `build.mk` are part of the build path.
- `docs/TECHNICAL.md` is the upstream technical reference.

## Implementation implications

A superficial change to an existing PC menu cannot establish a correct starting vocation. The mod needs to intercept or replace the original game creation/initialization sequence, while preserving:
- creation and protagonist save-state setup;
- first vocation ID and level-1 EXP/state;
- initial HP/MP and equipment/skill/spell eligibility;
- unlock/quest flags (including **Luminary**, which is an advanced vocation);
- later Alltrades Abbey access.

Next research task: locate concrete function names and call sites in the original decompilation symbol/config data. Do **not** commit guessed numeric vocation IDs, placeholder hooks that claim to work, or copyrighted code/data extracted from a ROM.

## Multiplayer limitation

Upstream documents remote networking for the game's original guest/host features, **not** automatic synchronized story quest progress from a new game. New-save co-op is a separate larger feature.

## Implementation status

Scaffolding and researched architecture only. No ROM, upstream code, compiled game, or patched logic has been checked into this repository. A playable modification still requires implementation and testing using a locally supplied game ROM.


## Verified build-time patch mechanism

Upstream `docs/TECHNICAL.md` documents `patches.txt` as instruction overrides applied by the static recompiler. The file format is:

```text
# <module> <address> <new ARM word>
```

Its existing example replaces an ARM branch instruction with a NOP in overlay 34; it is an anti-piracy memory-leak fix and **not** relevant to vocation selection. We must not modify or reuse this address.

Important: a small instruction patch may work for an initialization rule, but adding a six-option character-creation interface likely requires larger changes than a single instruction override. We need to find game logic before deciding between ARM patches, a hook in translated code, or a different approach.

The named symbol map at `config/usa/arm9/symbols.txt` was inspected and mostly uses generic `func_...` names, so keyword search alone cannot reliably identify the initialization point. No vocation function address has been verified yet.
