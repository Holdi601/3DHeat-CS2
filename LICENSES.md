# Licences and third-party components

Everything in this repository that was written for it is under the MIT licence in [`LICENSE`](LICENSE). Use it, change it,
ship it, commercially or not.

What the MIT licence cannot cover is what the tools are used with: the Python
packages they import, the models game capture runs, and the games they read.
Those carry their own terms, and they are listed here because the answer differs
by part, and the difference decides whether output may be used at work.

Every licence below was read off the package metadata or the model card in
September 2026, not recalled. Where a component's terms changed after that, the
source is what counts, not this file.

---

## CS2 — `cs2/`

### Software

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

### What it reads

A demo is the server's recording of a match; the map is part of the game. The
tool reads files the user has - their own matches, demos they downloaded, the
installed game - and what comes out is for their own analysis. Demos and
data derived from them are not this project's to redistribute, and not the
user's either: Valve has had a dataset built from professional demos taken
down. Sites that offer demos commonly forbid automated downloading in their
terms of use, which is why the tool reads demos from disk and fetches none.

---

## How geometry is obtained, and what that obliges

Not a licence question, but it belongs next to one: both are obligations that are
easy to breach without noticing. Three routes exist to a level's geometry, and
they are constrained by quite different things.

**Nothing here injects into a game process.** Frames come from Windows Graphics
Capture, the public API screen recorders use, and telemetry from feeds games
publish themselves. That is a deliberate constraint: injection into a title with
anti-cheat risks the account of whoever runs it.

**ReShade** was considered. Its depth buffer would make reconstruction far more
accurate, and ReShade itself is broadly tolerated — BattlEye states it bans only
actual cheats. But ReShade **disables depth-buffer access in multiplayer sessions
by design**, because depth access is a wallhack, and that is why it is tolerated
at all. So it is usable for single-player and offline titles, where it would be a
genuine improvement, and unavailable for exactly the always-online case an
analytics capture usually needs.

**Extracting geometry from shipped game files** — `.pak` archives and the like —
is a third route, and it is now built, as `gamefiles/`. An earlier
draft of this document ruled it out wholesale. That was too broad, and the
correction is worth recording because the reasoning matters more than the
conclusion.

A tool is not the same thing as a distribution. Extractors are published openly
and used widely — FModel, UModel, AssetRipper, Noesis — and the obvious
legitimate use is a developer reading *their own* game's build. Nothing about
parsing a container format is itself a circumvention.

The line that does matter is **encryption**, and it falls inside the tool rather
than around it. DMCA §1201(a)(2) reaches technologies, not only acts: a tool
whose purpose is to defeat an access control is in scope even if nobody
distributes a single extracted file. That is why the established extractors are
built the way they are — **they ship no keys and no key-recovery**. FModel cannot
open an encrypted archive until the user supplies an AES key they obtained
themselves. The tool reads containers; it does not break locks.

So the design, which is what was built:

- **Read unencrypted archives directly.** Ordinary parsing, no circumvention
  question arises. Every archive tested so far has been in this category.
- **For encrypted archives, take a key from the user and never recover one.** No
  bundled keys, no key extraction from the executable, no memory scraping.
  `pak.py` takes `aes_key=` and has no code path that obtains one.
- **Extract geometry, not assets to redistribute.** The output wanted here is a
  decimated collision or terrain mesh for spatial context, which is also the
  least of what an archive holds.

One consequence worth stating plainly: Frostbite's obfuscated table form is
*detected and declined*. Its key sits in the file itself, so it is obfuscation
rather than an access control and no key would be needed from anyone — but no
file on hand uses it, and implementing a format with nothing to check it against
produces something that looks like support and is not.

What remains the user's responsibility either way is the EULA of the game they
point it at. Those commonly prohibit reverse engineering and are enforceable
contracts; that obligation sits with whoever runs the tool, on whichever game,
and no design choice here discharges it.

---

## Sources

- [Depth Anything V2 model cards](https://huggingface.co/depth-anything) — licence per size
- [facebook/VGGT-1B](https://huggingface.co/facebook/VGGT-1B) — CC-BY-NC-4.0
- [ReShade — PCGamingWiki](https://www.pcgamingwiki.com/wiki/ReShade) — anti-cheat position
- [ReShade forum, depth buffer detection](https://reshade.me/forum/general-discussion/4083-depth-buffer-detection-modifications?start=1200) — multiplayer depth disabling
- [Reverse engineering and the law](https://ipwatchdog.com/2021/03/27/reverse-engineering-law-understand-restrictions-minimize-risks/) — EULA and DMCA position
- [DMCA §1201 anti-circumvention](https://copyrightalliance.org/education/copyright-law-explained/the-digital-millennium-copyright-act-dmca/section-1201-technology-protection/) — the tools provisions reach technologies, not only acts
- [FModel setup](https://modding.wiki/en/aewff/developers/fmodel) — established extractors require a user-supplied AES key rather than shipping one
- [facebook/VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial) — gated; access is granted per account, so it cannot be a default
- [Oodle Data Compression](http://www.radgametools.com/oodle.htm) — proprietary, no redistributable build, hence found rather than bundled
- [Review of Feed-forward 3D Reconstruction: DUSt3R to VGGT](https://arxiv.org/abs/2507.08448)

This document is a record of what the licences say. It is not legal advice, and
the commercial question for any particular use is one for whoever is answerable
for that use.
