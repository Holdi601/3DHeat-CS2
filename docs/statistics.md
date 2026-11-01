---
title: Statistics
nav_order: 6
---

# Statistics

What each player did in a match, and how each round went: the scoreboard and
the round list of the [match summary](output-match-json.md). Code:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Everything is counted from the match built as on
[Building a match](building-matches.md): its kill records, its damage (health
lost, enemies only), its blinds (enemies only) and its rows.

## The conventions

Where the game itself does not define a number, these are the definitions.
They are also written into every summary under `conventions`.

| Term | Definition |
|---|---|
| **Trade** | A death is *traded* when its killer is killed by one of the victim's teammates within **5 s**; that kill is a *trade kill*. |
| **Opening** | The round's first kill of an enemy while it is live. A teamkill, a suicide or a death to the world before it is passed over. |
| **KAST** | The share of rounds in which a player got a **K**ill, an **A**ssist (a flash assist counts), **S**urvived, or was **T**raded. |
| **Damage** | Health actually lost, enemies only: a 137 damage headshot on a player with 40 health is 40. |
| **Clutch** | Being the last player alive on a side with enemies still standing; won when the side wins the round. |
| **Buy** | Per side, from the average equipment value at the end of freeze time: the first round of each regulation half is a pistol round (round 1, and the round after the half, as long as the match played it), overtime has none; then under $1,500 eco, under $4,000 force, otherwise full. |

## Who started each round

Several numbers need to know who played a round. A round's **starting
players** are, per side, every player with a live position row within one
second of the earliest position of that round (that is, in the first second
after freeze time ended). A player's **rounds played** is the number of
rounds they started. If a player started none (they never had such a row),
the match's round count is used instead, so that no division is by zero.

## The scoreboard line

One entry per player (see [the summary](output-match-json.md#players) for the
field names). "Enemy kill" below means a kill with an attacker, not a
teamkill, and not a suicide (the victim's own).

| Field | Counts |
|---|---|
| `kills` | enemy kills, of the live and the after phase |
| `deaths` | every death: by enemies, teammates, oneself or the world |
| `assists` | enemy kills this player assisted without a flash (the assister must not be the killer) |
| `flashAssists` | enemy kills this player assisted with a flash |
| `diff` | kills - deaths |
| `adr` | damage (health lost, enemies only, both phases) / rounds played, one decimal |
| `kast` | 100 x (rounds with a kill, an assist or flash assist, survival or a traded death) / rounds played, one decimal. *Survival* is: a starting player of the round who did not die in it, in either phase. |
| `headshotPct` | 100 x headshot kills / kills, one decimal; 0 with no kills |
| `openingKills`, `openingDeaths` | opening duels won and lost |
| `tradeKills` | kills that traded a teammate's death |
| `tradedDeaths` | deaths that were traded |
| `multiKills` | rounds with 2, 3, 4 and 5 enemy kills (`2k`, `3k`, `4k`, `5k`); more than five counts as `5k`. Both phases count. |
| `clutches`, `clutchesWon` | clutches played and won (below) |
| `utilityDamage` | damage done with HE grenades, molotovs and incendiaries, one decimal |
| `enemiesFlashed` | enemies blinded for **at least 1.0 s** by this player's flashes |
| `plants`, `defuses` | bomb plants and defuses (rows of the table) |
| `teamkills` | teammates killed. A suicide - attacker and victim the same player, an own grenade say - is not one: it is only a death. |
| `roundsPlayed` | rounds started, as above |

Players are listed by team name (alphabetically), and within a team by
`diff`, then by `kills`, best first.

Notes on the edges:

- A kill in the after phase - the winners hunting a saving player - counts
  as a kill, a death, for ADR, multi-kills and KAST like any other.
- Wallbangs are counted per player internally but not written to the
  summary; each kill in the round list says whether it was one.
- The KAST *traded* part credits the victim of a traded death in that round.
- Teamkills and suicides add a death to the victim but no kill to anyone; a
  teamkill adds to the killer's `teamkills`, a suicide to nothing else.

## Clutches

For each round, the starting players of both sides are taken as alive, and
the round's live kills are walked in order. After each death the victim is
removed, and every side is looked at: a side with exactly **one** player
left, and at least one enemy still alive, is a clutch for that player
**against** the number of enemies alive at that moment. Each player has at
most one clutch per round; it is **won** when that player's side won the
round.

Consequences of the definition:

- Both sides can have a clutch in one round. If a side is down to one first
  (a 1v3, say) and the other side is then also brought down to one, the
  second player is in a 1v1 clutch of their own.
- `against` is the count when the player became the last one, not at the end.
- Kills of the after phase are not walked, so they neither start a clutch
  nor change one.

## Survivors

A round's **survivors** are, per side, its starting players minus everyone
who died while it was live. A player killed in the after phase while saving
is still a survivor in the round list - but did not *survive* for KAST.

## The round list

Each round of the summary carries its result, score, sides, economy, plant,
survivors, clutches and its kills in order; see
[The match summary](output-match-json.md#rounds).

## The text scoreboard

`python -m heat3d_cs2 scoreboard <match.json>` prints these numbers per team;
see [Commands](commands.md#scoreboard---a-summary-as-text).
