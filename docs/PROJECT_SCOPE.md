# Project scope

## Goal
Build a personal DQIX modification compatible with a legitimate, locally supplied Dragon Quest IX game copy, prioritizing **starting vocation choice at character creation**. Online multiplayer is a separate compatibility goal.

## Requirements
- At character creation, offer exactly six default vocations: Warrior, Martial Artist, Mage, Priest, Thief, Minstrel.
- Chosen vocation begins at level 1 with canonical starting stats, vocation experience, equipment rules, skill access and relevant initial inventory determined by the game’s existing mechanisms.
- Preserve appearance/name customization.
- Keep advanced vocations locked behind their original unlock quests. In-scope list to verify against game data: Gladiator, Paladin, Ranger, Armamentalist, Sage, Luminary.
- Preserve Alltrades Abbey vocation switching and normal story progression.
- Keep original balance unless a change is required for correct initialization.
- Retain multiplayer up to the game’s supported 4-player party; require matching game/mod builds between players.

## Non-goals for the first milestone
- Rewriting the campaign to support synchronized story progression from fresh saves.
- Bypassing story gates to make cooperative play available from the opening scene.
- Including proprietary game files or distributing a modified game executable / ROM.
- Claiming online co-op is functional without real multi-machine tests.

## Acceptance criteria: vocation creation
1. Fresh save displays six selectable starting vocations.
2. Each selection results in correct level-1 class stats, HP/MP, learned abilities, spell access, equipment permissions and vocation-specific data.
3. New saves reload consistently and don't corrupt story flags.
4. Advanced vocations remain unavailable before original unlocks.
5. Alltrades Abbey still works as expected.
6. Both single-player and (when available) multi-player saves remain compatible or clearly versioned.

All behavior remains **planned, not implemented**, until source inspection and testing prove otherwise.
