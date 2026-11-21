"""
Reads files out of a Valve package (`.vpk`, version 1 or 2): the `_dir.vpk` holds the tree of every file with its
archive number, offset and length (or the bytes themselves, when they are small), the numbered `_NNN.vpk` archives
hold the rest. Used for the text files the catalogue needs (item and weapon definitions, the localisation); models
go through Source2Viewer, which reads packages itself.
"""

from __future__ import annotations

import struct
from pathlib import Path


class Vpk:
    def __init__(self, dir_path: str | Path):
        self.path = Path(dir_path)
        self.entries: dict[str, tuple[int, int, int, bytes]] = {}
        with self.path.open("rb") as fh:
            sig, ver, tree = struct.unpack("<III", fh.read(12))
            if sig != 0x55AA1234:
                raise ValueError(f"{self.path.name}: not a Valve package")
            head = 12 if ver == 1 else 28
            if ver == 2:
                fh.read(16)
            data = fh.read(tree)
        self._data_at = head + tree
        o = 0

        def cstr() -> str:
            nonlocal o
            e = data.index(b"\0", o)
            s = data[o:e].decode("utf-8", "replace")
            o = e + 1
            return s

        while True:
            ext = cstr()
            if not ext:
                break
            while True:
                folder = cstr()
                if not folder:
                    break
                while True:
                    name = cstr()
                    if not name:
                        break
                    _crc, pre, arc, off, ln, _end = struct.unpack_from("<IHHIIH", data, o)
                    o += 18
                    preload = data[o:o + pre]
                    o += pre
                    full = (f"{folder}/" if folder.strip() else "") + name + (f".{ext}" if ext.strip() else "")
                    self.entries[full.lower()] = (arc, off, ln, preload)

    def names(self, prefix: str = "", suffix: str = "") -> list[str]:
        p, s = prefix.lower(), suffix.lower()
        return [n for n in self.entries if n.startswith(p) and n.endswith(s)]

    def read(self, name: str) -> bytes:
        arc, off, ln, preload = self.entries[name.lower()]
        if not ln:
            return preload
        if arc == 0x7FFF:
            src = self.path
            off += self._data_at
        else:
            src = self.path.with_name(self.path.name.replace("_dir.vpk", f"_{arc:03d}.vpk"))
        with src.open("rb") as fh:
            fh.seek(off)
            return preload + fh.read(ln)
