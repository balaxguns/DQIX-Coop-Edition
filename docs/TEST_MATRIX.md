# Manual test matrix

Statuses: NOT RUN / PARTIAL / PASS / FAIL / BLOCKED. All tests begin at NOT RUN.

| ID | Test | Status |
| --- | --- | --- |
| C01 | Create Warrior at level 1; verify stats, equipment, skills | NOT RUN |
| C02 | Create Martial Artist at level 1; verify stats, equipment, skills | NOT RUN |
| C03 | Create Mage at level 1; verify stats, equipment, spells | PARTIAL — Mage displays; user reports stats look appropriate, but spells appear absent (Frizz should be learned at level 1); equipment not tested |
| C04 | Create Priest at level 1; verify stats, equipment, spells | NOT RUN |
| C05 | Create Thief at level 1; verify stats, equipment, skills | NOT RUN |
| C06 | Create Minstrel at level 1; compare original baseline | NOT RUN |
| S01 | Save and reload each creation result | NOT RUN |
| P01 | Level up each initial vocation normally | NOT RUN |
| P02 | Advanced vocations stay quest-locked | NOT RUN |
| P03 | Alltrades Abbey changing still works | NOT RUN |
| N01 | Two machines connect using matching builds | NOT RUN |
| N02 | Four players connect and maintain a session | NOT RUN |
| N03 | Character class data remains intact in guest session | NOT RUN |
| N04 | Document original guest story-progression restrictions | NOT RUN |

Log game region, upstream commit, mod commit, build environment, test save type, and any failure details before marking PASS.

## Playtest report — 2026-11-10

User confirmed that an experimental Mage-modified `dqix.sav` loads and displays the hero as **Mage** in the game. This establishes **vocation field recognition only**; it does not yet establish correct class stats, spells, equipment restrictions, level-up behavior, save/reload persistence, or an in-game creation UI. All those remain open. No proprietary save or ROM was committed.

## Follow-up observation — Mage spell check

User reports Mage stats appear appropriate but does not believe any spells are unlocked. Independent DQIX Mage spell lists specify **Frizz at Mage level 1**, so the possible missing spell is a functional blocker until checked in the game's Spells menu or battle command. This may indicate that merely changing the current-vocation save byte is not equivalent to the native job-change initialization path. Do not mark C03 PASS. References: https://www.dq9encyclopedia.com/en/guide/mage and https://dragon-quest.org/wiki/List_of_spells_in_Dragon_Quest_IX
