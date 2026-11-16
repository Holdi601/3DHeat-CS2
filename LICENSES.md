# Licences and third-party components

Everything in this repository that was written for it is under the MIT licence in [`LICENSE`](LICENSE). Use it, change it,
ship it, commercially or not.

What the MIT licence cannot cover is what the tool is used with: the Python
packages it imports and the program the map export runs. Those carry their own
licences, listed here.

Every licence below was read off the package metadata in September 2026, not
recalled. Where a component's terms changed after that, the source is what
counts, not this file.

---

## Software

| Package | Licence | Note |
|---|---|---|
| demoparser2 | MIT | Reading the demos |
| pyarrow | Apache-2.0 | Writing Parquet |
| pandas, numpy | BSD-3-Clause | |
| pytest | MIT | Development only |

All permissive. The map export runs **Source2Viewer's command line**
([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat),
MIT) as a separate program the user installs; it is not bundled and nothing
of it is copied here.

## What it reads

A demo is the server's recording of a match; the map is part of the game. The
tool reads files the user has - their own matches, demos they downloaded, the
installed game - and what comes out is for their own analysis. Demos and data
derived from them are not for redistribution. The tool reads demos from disk
and downloads none.

## The map's geometry

The map export reads the map's own `.vpk` from the installed game. Those
archives are not encrypted: reading them is ordinary parsing - no keys, no
injection into the game, nothing read from its memory. What is taken is the
world's collision mesh, for spatial context under a heatmap, which is also the
least of what the archive holds; it is written to the user's disk and never
shipped with this repository. Nothing from the game ships with the tool: no
game files, no game code, no DLLs.

3DHeat CS2 is not affiliated with or endorsed by Valve. Counter-Strike 2 and
related names and trademarks belong to their owners. Rights holders: open an
issue at <https://github.com/Holdi601/3DHeat-CS2/issues> - we respond quickly and remove
anything on request.

---

## Sources

- [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) — Source2Viewer, MIT
