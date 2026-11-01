# Licences and third-party components

Everything in this repository that was written for it is under the MIT licence in [`LICENSE`](LICENSE). Use it, change it,
ship it, commercially or not.

What the MIT licence cannot cover is what the tool is used with: the Python
packages it imports, the program the map export runs, and the game whose demos
and maps it reads. Those carry their own terms, and they are listed here because
they decide what may be done with the output.

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
installed game - and what comes out is for their own analysis. Demos and
data derived from them are not this project's to redistribute, and not the
user's either: Valve has had a dataset built from professional demos taken
down. Sites that offer demos commonly forbid automated downloading in their
terms of use, which is why the tool reads demos from disk and fetches none.

## The map's geometry

The map export reads the map's own `.vpk` from the installed game. Those
archives are not encrypted: reading them is ordinary parsing, and nothing is
circumvented - no keys, no injection into the game, nothing read from its
memory. What is taken is the world's collision mesh, for spatial context
under a heatmap, which is also the least of what the archive holds; it is
written to the user's disk and never shipped with this repository.

What remains the user's responsibility is the game's EULA. Such agreements
commonly prohibit reverse engineering and are enforceable contracts; that
obligation sits with whoever runs the tool, and no design choice here
discharges it.

---

## Sources

- [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) — Source2Viewer, MIT
- [Reverse engineering and the law](https://ipwatchdog.com/2021/03/27/reverse-engineering-law-understand-restrictions-minimize-risks/) — EULA and DMCA position
- [DMCA §1201 anti-circumvention](https://copyrightalliance.org/education/copyright-law-explained/the-digital-millennium-copyright-act-dmca/section-1201-technology-protection/) — the tools provisions reach technologies, not only acts

This document is a record of what the licences say. It is not legal advice, and
the commercial question for any particular use is one for whoever is answerable
for that use.
