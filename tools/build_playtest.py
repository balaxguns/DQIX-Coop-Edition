#!/usr/bin/env python3
"""Build a separate DQIX-Coop Windows test installation from your own ROM.

Run from Build DQIX Coop Playtest.bat on Windows. This downloads only public
source code, copies (never moves) your locally selected .nds cartridge dump,
installs the six-option Game menu patch, and runs upstream's normal BUILD.bat.

It will NOT modify your existing installed DQIX Enhanced game or save.
"""
import io
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

UPSTREAM_COMMIT = "86ff9b1ce6128a52f1e83d110b5c893043df5159"
UPSTREAM_URL = (
    "https://github.com/sackchief/dqix-enhanced/archive/"
    + UPSTREAM_COMMIT + ".zip"
)
INSTALL_NAME = "DQIX-Coop-Playtest"


def extract_verified_zip(data, destination):
    """Reject absolute paths and traversal; do not follow zip symlink entries."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = archive.infolist()
        if not files:
            raise ValueError("The upstream download is empty")
        top = None
        for info in files:
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or ":" in info.filename or "\\" in info.filename):
                raise ValueError("Unsafe upstream ZIP path")
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError("Refusing ZIP symbolic link")
            if top is None:
                top = path.parts[0]
            if path.parts[0] != top:
                raise ValueError("Unexpected archive structure")
        destination.mkdir(parents=True, exist_ok=False)
        for info in files:
            path = PurePosixPath(info.filename)
            relative = Path(*path.parts[1:])
            if not relative.parts:
                continue
            output = destination / relative
            if info.is_dir():
                output.mkdir(parents=True, exist_ok=True)
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, output.open("xb") as target:
                    shutil.copyfileobj(source, target)
    if not (destination / "BUILD.bat").is_file():
        raise ValueError("Downloaded source is missing BUILD.bat")


def prepare(rom, destination, project):
    if destination.exists():
        raise ValueError(
            f"The playtest folder already exists: {destination}. "
            "It was not modified. Choose another parent folder."
        )
    if not rom.is_file() or rom.suffix.lower() != ".nds":
        raise ValueError("Select a local .nds dump of your own DQIX cartridge")
    if rom.stat().st_size < 1024 * 1024:
        raise ValueError("Selected .nds is too small to be a normal DS game")
    if not (project / "tools" / "install_native_hook.py").is_file():
        raise ValueError("Expected DQIX-Coop source tools were not found")
    print("Downloading pinned DQIX Enhanced SOURCE (no game data)...", flush=True)
    with urllib.request.urlopen(UPSTREAM_URL, timeout=120) as response:
        data = response.read(80 * 1024 * 1024 + 1)
    if len(data) > 80 * 1024 * 1024:
        raise ValueError("Upstream ZIP exceeds size limit")
    try:
        extract_verified_zip(data, destination)
        # The tools modify only this newly extracted source copy.
        subprocess.run([sys.executable, str(project / "tools" / "install_native_hook.py"),
                        str(destination)], check=True)
        subprocess.run([sys.executable, str(project / "tools" / "install_game_menu.py"),
                        str(destination)], check=True)
        rom_dir = destination / "rom"
        rom_dir.mkdir(exist_ok=True)
        shutil.copy2(rom, rom_dir / "dqix.nds")
    except BaseException:
        # Keep the partial folder for diagnosing failures, but never touch the
        # original ROM. Do not delete arbitrary files if a user interrupts.
        raise
    return destination / "BUILD.bat"


def main():
    if sys.platform != "win32":
        raise SystemExit("This builder is for Windows only.")
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "DQIX-Coop-Edition test builder",
        "This creates a SEPARATE DQIX-Coop-Playtest folder.\n\n"
        "Your existing DQIX Enhanced installation and original save will "
        "not be modified. Choose the .nds dump from your own cartridge.")
    filename = filedialog.askopenfilename(
        title="Select YOUR Dragon Quest IX .nds ROM",
        filetypes=[("Nintendo DS ROM", "*.nds"), ("All files", "*.*")])
    if not filename:
        print("Cancelled. Nothing changed.")
        return 0
    parent = filedialog.askdirectory(
        title="Where should the SEPARATE test folder be created?")
    if not parent:
        print("Cancelled. Nothing changed.")
        return 0
    rom = Path(filename)
    destination = Path(parent) / INSTALL_NAME
    project = Path(__file__).resolve().parents[1]
    try:
        build = prepare(rom, destination, project)
    except (OSError, ValueError, zipfile.BadZipFile,
            urllib.error.URLError, subprocess.CalledProcessError) as e:
        messagebox.showerror("Playtest preparation failed", str(e))
        print("ERROR:", e)
        return 1
    print("\nSeparate test source prepared at:", destination, flush=True)
    print("Starting DQIX Enhanced's original Windows build script.", flush=True)
    print("This builds from YOUR .nds locally; no game files are uploaded.", flush=True)
    result = subprocess.run(["cmd.exe", "/c", str(build)], cwd=destination)
    if result.returncode != 0:
        print("Upstream build failed (code", result.returncode, ")")
        messagebox.showerror("Build failed",
                             "The Windows build did not complete. "
                             "The source files remain in the playtest folder.")
        return result.returncode
    exe = destination / "game" / "dqix.exe"
    if not exe.exists():
        messagebox.showwarning(
            "Check build output",
            "Build finished but game/dqix.exe was not found. "
            "Check the upstream build console for its output path.")
    else:
        messagebox.showinfo(
            "DQIX-Coop build created",
            "Your separate test game was built.\n\n"
            "Copy an early Level 1 MINSTREL test save into this playtest "
            "game folder as dqix.sav, keeping your original safe.\n\n"
            "Launch the test game and choose Game > Starting vocation.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("Unexpected error:", error)
        sys.exit(1)
