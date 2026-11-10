#!/usr/bin/env python3
"""DQIX-Coop-Edition experimental save selector.

Uses only Python's standard library. It NEVER modifies the chosen source file.
It creates a separate result that must be tested in an isolated game folder.
This is not yet an in-game creation menu.
"""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from set_starting_vocation import patch_save, SaveError, VOCATIONS, SLOT_SIZE,     checksums_ok, CHARACTER_OFFSET, CHARACTER_SIZE, CURRENT_VOCATION,     STANDBY_COUNT, PARTY_COUNT, SAVE_EXISTS, LEVELS, EXPS, u32

LABELS = {
    "warrior": "Warrior",
    "martial-artist": "Martial Artist",
    "mage": "Mage",
    "priest": "Priest",
    "thief": "Thief",
}


def preview(raw):
    """Read-only summary, no proprietary data printed or sent anywhere."""
    if len(raw) != SLOT_SIZE * 2:
        return "Not a 64 KiB DQIX save"
    lines = []
    for index in (0, 1):
        data = raw[index * SLOT_SIZE:(index + 1) * SLOT_SIZE]
        if not checksums_ok(data):
            lines.append(f"Slot {index}: bad checksum")
            continue
        if not data[SAVE_EXISTS] & 1:
            lines.append(f"Slot {index}: empty")
            continue
        standby = data[STANDBY_COUNT]
        party = data[PARTY_COUNT]
        if standby > 8 or party < 1 or standby + party > 13:
            lines.append(f"Slot {index}: unsupported party layout")
            continue
        hero = CHARACTER_OFFSET + CHARACTER_SIZE * standby
        current = data[hero + CURRENT_VOCATION]
        level = data[hero + LEVELS + current] if current < 12 else None
        exp = u32(data, hero + EXPS + current * 4) if current < 12 else None
        lines.append(f"Slot {index}: vocation ID {current}, level {level}, EXP {exp}")
    return "\n".join(lines)


def main():
    root = tk.Tk()
    root.title("DQIX-Coop-Edition | Experimental Vocation Selector")
    root.geometry("600x350")
    root.minsize(500, 310)
    root.columnconfigure(0, weight=1)
    source = tk.StringVar()
    vocation = tk.StringVar(value="mage")
    status = tk.StringVar(value="Select a disposable, backed-up DQIX Enhanced save file.")

    panel = ttk.Frame(root, padding=18)
    panel.grid(sticky="nsew")
    panel.columnconfigure(0, weight=1)
    ttk.Label(panel, text="Experimental starting-vocation selector", font=("Segoe UI", 14, "bold")).grid(sticky="w")
    ttk.Label(panel, text="Creates a NEW .sav file. Does not change your original game or save.").grid(sticky="w", pady=(4, 12))
    ttk.Label(panel, text="Original save:").grid(sticky="w")
    entry = ttk.Entry(panel, textvariable=source, width=70)
    entry.grid(row=3, sticky="ew", pady=(4, 5))

    def browse():
        selected = filedialog.askopenfilename(filetypes=[("DQIX save", "*.sav"), ("All files", "*.*")])
        if selected:
            source.set(selected)
            try:
                status.set(preview(Path(selected).read_bytes()))
            except OSError as error:
                status.set(str(error))

    ttk.Button(panel, text="Browse for a copy of dqix.sav", command=browse).grid(sticky="w")
    ttk.Label(panel, text="Select the vocation for testing:").grid(sticky="w", pady=(15, 3))
    ttk.Combobox(panel, textvariable=vocation, values=list(LABELS.values()),
                 state="readonly", width=25).grid(sticky="w")
    vocation.set("Mage")

    def generate():
        try:
            path = Path(source.get())
            choice = next(key for key, label in LABELS.items() if label == vocation.get())
            destination = filedialog.asksaveasfilename(
                title="Save a NEW test file", defaultextension=".sav",
                initialfile="dqix-test-" + choice + ".sav",
                filetypes=[("DQIX save", "*.sav")])
            if not destination:
                return
            target = Path(destination)
            if path.resolve() == target.resolve():
                raise SaveError("Cannot overwrite your original save")
            if target.exists():
                raise SaveError("Output file already exists; choose a new name")
            modified = patch_save(path.read_bytes(), choice)
            with target.open("xb") as f:
                f.write(modified)
            messagebox.showinfo("Test save created",
                                f"Created a separate test save:\n{target}\n\n"
                                "Only use this in an ISOLATED test game folder.")
        except (OSError, SaveError, StopIteration) as error:
            messagebox.showerror("No changes made", str(error))

    ttk.Button(panel, text="Create separate test save", command=generate).grid(sticky="w", pady=(16, 8))
    ttk.Label(panel, textvariable=status, wraplength=540, foreground="#444").grid(sticky="w")
    root.mainloop()


if __name__ == "__main__":
    main()
