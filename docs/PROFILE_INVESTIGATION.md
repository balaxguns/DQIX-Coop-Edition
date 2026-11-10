# Function profile investigation

A **real Python tool** is now committed at [tools/compare_profiles.py](../tools/compare_profiles.py), along with [unit tests](../tests/test_compare_profiles.py).

It compares two DQIX Enhanced function-entry profiles, ranks ARM9 functions that ran more often during character creation, and displays their module-independent addresses. It never reads a game ROM, save, or proprietary game data.

## Using profiles (development-only)

Upstream `runtime/dispatch.c` supports the `DQIX_PROF=first_frame,last_frame` environment variable, and `runtime/main.c` emits the profile in its shutdown report to stderr. The default print limit is 50 functions, adjustable with `DQIX_PROF_TOP`.

Capture two text reports:
- `baseline.txt`: game/menu activity unrelated to making a character
- `creation.txt`: a similar-length execution covering character creation

Run:

```powershell
python tools/compare_profiles.py baseline.txt creation.txt --top 100
python -m unittest discover -s tests -v
```

The tool's output is a **shortlist of candidates only**, not a proven character/vocation implementation. Because profiles count many general game functions and only the top functions are shown by default, the method needs controlled recordings and possibly a higher `DQIX_PROF_TOP`.

An accurate compare requires matched frame windows and ideally repeated independent captures to separate UI noise from candidate initialization paths. We cannot yet gather those captures using only the GitHub connector, because generated local code and execution happen on the player's PC.

## Source evidence
- [Upstream runtime profiler](https://github.com/sackchief/dqix-enhanced/blob/main/runtime/dispatch.c)
- [Upstream shutdown reporting](https://github.com/sackchief/dqix-enhanced/blob/main/runtime/main.c)
- [Recompiler wrapper mechanism](https://github.com/sackchief/dqix-enhanced/blob/main/recomp/build.py)
- [Existing example wrapper map](https://github.com/sackchief/dqix-enhanced/blob/main/wrap.txt)

**State:** tool code committed; no successful DQIX game profiling capture or live game patch yet. Unit tests can be run without game assets.
