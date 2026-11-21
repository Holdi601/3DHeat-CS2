# Changelog

## 1.0.6

- `catalog` and `models` read the installed game's `weapons.vdata` through Source2Viewer 21.1; `--vdata` stays as an
  override for older builds.
- `models`: the AUG, C4 and R8 Revolver, and the knives, grenades and kit (armour, defuser, health shot), whose
  world models only `weapons.vdata` names: 211 models in all. A weapon's world model is read from one of its two
  bodies, not both on top of each other.

## 1.0.5

- `catalog`: every weapon, item and agent of the installed game as `catalog.json` (class, side, numbers; the
  agents' units), for the viewer's names and order.
- `models`: the agents' and weapons' models of the installed game as a local model pack (`model-pack.json` and a
  `.glb` per unit, three levels of detail; the agents' hit groups), drawn by the viewer in place of its figures.

## 1.0.4

- `layouts <map>|all -o <folder>`: a map's bomb sites and buy zones (their outlines and heights), hostage spots
  and rescue zones, and the T and CT spawns, from the map's own entities, as `<map>.layouts.json` beside its
  `.glb`; `competitive`, and `wingman` where the map has its own spawns for it. The viewer draws them on the map.

## 1.0.3

- The table says the outcome on every row, as the viewer's outcome contract has it: `matchWon` (0/1, the row's
  team won the match, where the recording shows the end) and `roundEndReason` (`elimination`, `bomb`, `defuse`,
  `time`, `surrender`, `draw`); the match document names the match's `winner` and how it is known.
- `scoreboard` reads the match document straight from a `.3dheat` container, as well as from a loose
  `.match.json`.
- Documentation: a "Before you start" page for newcomers, a generated command and column reference
  (`tools/gen_docs_reference.py`), the release checklist (`docs/maintaining.md`), and made-up names in
  every example.
- README: a quick start for new users.

## Docs

Where each feature is documented (<https://holdi601.github.io/3DHeat-CS2/>):

| Feature | Page |
|---|---|
| Installing, first run | [Before you start](docs/before-you-start.md), [Installing](docs/installing.md) |
| `demos`: demos into one file a match | [Commands](docs/commands.md#demos---demos-into-tables-and-match-documents) |
| Parts of a match, chains, the clock, rounds | [Building a match](docs/building-matches.md) |
| What is read from a demo | [Reading a demo](docs/reading-demos.md) |
| ADR, KAST, trades, clutches, economy | [Statistics](docs/statistics.md) |
| The table's columns, the player's state, round pay | [The heatmap table](docs/output-table.md) |
| The match document | [The match document](docs/output-match-json.md) |
| `.3dheat` containers, `--loose`, sidecars, completeness | [One file a match](docs/output-container.md) |
| `map`: a map's collision mesh | [Map export](docs/map-export.md), [Commands](docs/commands.md#map---a-maps-geometry-as-glb) |
| `scoreboard` | [Commands](docs/commands.md#scoreboard---a-match-as-text) |
| Loading it in the viewer | [Using it with 3DHeat](docs/using-with-3dheat.md) |
| Every option and column, generated | [Reference](docs/cli-reference.md) |
| Release checks | [Updates](docs/updates.md), [Maintaining](docs/maintaining.md) |
