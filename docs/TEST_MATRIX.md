# Manual test matrix

Statuses: NOT RUN / PARTIAL / PASS / FAIL / BLOCKED. All tests begin at NOT RUN.

| ID | Test | Status |
| --- | --- | --- |
| C01 | Create Warrior at level 1; verify stats, equipment, skills | NOT RUN |
| C02 | Create Martial Artist at level 1; verify stats, equipment, skills | NOT RUN |
| C03 | Create Mage at level 1; verify stats, equipment, spells | PARTIAL — Mage displays, stats appear appropriate, and Frizz is available; equipment restrictions not yet tested; Frizz persisted after save/reload |
| C04 | Create Priest at level 1; verify stats, equipment, spells | NOT RUN |
| C05 | Create Thief at level 1; verify stats, equipment, skills | NOT RUN |
| C06 | Create Minstrel at level 1; compare original baseline | NOT RUN |
| S01 | Save and reload each creation result | PARTIAL — Mage test save reloaded with Frizz still available; other vocations not tested |
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

User subsequently confirmed **Frizz is available** for their level-1 Mage, correcting the earlier uncertain observation that spells might be missing. This supports the expected Mage spell availability. Equipment restrictions and level-up behavior have not yet been tested. User subsequently confirmed Frizz persists after saving and reopening the game. Do not mark C03 PASS yet.

## Mage persistence confirmation — 2026-11-10

User reported that after saving, closing, and reopening DQIX Enhanced, the Mage character still had **Frizz**. This verifies persistence of that spell across a save/reload cycle, but the user did **not explicitly recheck the character's displayed vocation** after reopening, so a complete vocation persistence claim still needs confirmation. In-game creation UI is not yet implemented.
