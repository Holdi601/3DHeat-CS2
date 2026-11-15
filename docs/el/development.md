---
title: "Ανάπτυξη"
nav_order: 15
lang: "el"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Ανάπτυξη {#development}

## Δομή {#layout}

| Διαδρομή | Τι είναι |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: ο έλεγχος έκδοσης, μετά η γραμμή εντολών |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | οι εντολές και οι επιλογές· η ομαδοποίηση των αρχείων demo σε αγώνες· η δεξαμενή εργασιών |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | ένα αρχείο demo μέσω του demoparser2 σε ένα `RawPart` - [Ανάγνωση demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | τα κομμάτια, οι αλυσίδες, το ρολόι, οι γύροι, οι ομάδες, οι γραμμές, οι φόνοι, η ζημιά, οι τυφλώσεις - [Δημιουργία αγώνα](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | τα αποτελέσματα των γύρων, το σκορ, το έγγραφο αγώνα, το σκορ κειμένου - [Στατιστικά](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | ο πίνακας Parquet με τις υποδείξεις `heat3d`, και το JSON - [Ο πίνακας χάρτη θερμότητας](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | εύρεση του CS2 και του Source2Viewer, το collision mesh στο πλαίσιο του προβολέα - [Εξαγωγή χάρτη](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | ένας μικρός αναγνώστης και εγγραφέας δυαδικού glTF (καμία εξάρτηση πέρα από το numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | ο έλεγχος έκδοσης και ο ενημερωτής - [Ενημερώσεις](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | οι δοκιμές και το συνθετικό demo |
| `VERSION` | η έκδοση, μία γραμμή |

Η ροή των δεδομένων:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Χρήση από Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # the heatmap table as a pandas DataFrame
    kills = match.kills        # one row per death, with every flag
    doc = summary(match)       # the .match.json document as a dict
    write(match, "out/" + match.map)
```

Τα `Match.kills`, `Match.damage` και `Match.blinds` είναι πίνακες pandas με περισσότερα από όσα έχουν οι έξοδοι -
θέσεις του δολοφόνου και του θύματος και τοποθεσίες ανά φόνο, ζημιά ανά χτύπημα ως `utility` - για δικές σας αναλύσεις.

## Δοκιμές {#tests}

```bash
python -m pytest
```

Το `pytest.ini` τρέχει το `tests/` αθόρυβα. Οι δοκιμές δεν χρειάζονται demo, παιχνίδι ή Source2Viewer:
το [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) φτιάχνει ένα demo με το χέρι,
όπως θα το έδινε το demoparser2 - δύο γύροι, δύο παίκτες ανά πλευρά (`ace`, `ash` της ομάδας Alpha· `bob`, `ben` της
Bravo), αρκετά μικρό ώστε κάθε απάντηση να είναι γνωστή:

- Γύρος 1, νίκη των T με εξόντωση: ο ace σκοτώνει τον bob με headshot (το άνοιγμα), ο ben σκοτώνει τον ace 1,9 s
  αργότερα (ένα trade· ο θάνατος του bob εκδικείται), ο ash σκοτώνει τον ben 3,1 s μετά - μόνος του ενάντια σε έναν,
  ένα clutch που κερδήθηκε.
- Γύρος 2, νίκη των T από τη βόμβα: ο ash φυτεύει στο A, κανείς δεν πεθαίνει, η βόμβα εκρήγνυται.

Το `fixtures.halves` φτιάχνει έναν μακρύτερο αγώνα από άδειους γύρους, με τις ομάδες στις πρώτες τους πλευρές ή
ανταλλαγμένες, με ή χωρίς τον μετρητή παράτασης του παιχνιδιού, για το μήκος του ημιχρόνου και τους γύρους πιστολιού.

Το [`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) ελέγχει πάνω του: τον
νικητή, τον λόγο, το σκορ και τις πλευρές κάθε γύρου· το ρολόι που ξεκινά από τον αγώνα· την οικονομία και το φύτεμα
(τον χρόνο μέσα στον γύρο, την τοποθεσία του, την έκρηξη της βόμβας)· ότι η πλευρά ενός φυτέματος είναι πάντα ένα
γράμμα ή κενό, ποτέ αριθμός οντότητας· μια ισοπαλία που αποφασίζεται χωρίς νικητή· τους γύρους πιστολιού από το
σημείο όπου αλλάζουν πλευρές, με την παράταση εκτός, και μόνο τον γύρο 1 χωρίς αλλαγή· ομάδες χωρίς ονόματα κλαμπ
(`Started T` / `Started CT`)· ανοίγματα, trades και σημαίες· μια αυτοκτονία που δεν είναι teamkill, και το άνοιγμα
που περνά στον πρώτο φόνο εχθρού· τα `noscope` και `attackerBlind` στον πίνακα και στο έγγραφο αγώνα· τη ζημιά ως
υγεία που χάθηκε (60, και μετά 40 από ένα headshot 137 σε 40 υγεία)· τους αριθμούς του σκορ και το KAST· τα clutch·
το σκορ κειμένου· τα γεγονότα του πίνακα και πού βρίσκονται (μια έκρηξη χωρίς τοποθεσία δικιά της, η τοποθεσία του
ρίχτη στο `throwerPlace`· η έκρηξη είναι της ομάδας που φύτεψε)· ότι οι θέσεις είναι ζωντανές, με ετικέτες και
μοναδιαία διανύσματα βλέμματος· ότι το γραμμένο αρχείο έχει τις υποδείξεις του· ότι τα κομμάτια μπαίνουν σε σειρά,
όποια και να είναι τα ονόματά τους· ένα επανεκκινημένο ρολόι διακομιστή που συνεχίζει ακόμα· και τις διπλές γραμμές
ενός επαναφερμένου γύρου, λυμένες στη γραμμή που οδηγεί προς τα μπροστά.

Το [`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) ελέγχει ότι τα demo μέσα σε
φακέλους βρίσκονται ανεξάρτητα από το πώς γράφεται το `.dem`, και ότι ένας αγώνας μετράει ως γραμμένος μόνο με τον
πίνακα και το έγγραφο αγώνα του μαζί.

Το [`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) ελέγχει τις
μετατροπές πλαισίου (τα μέτρα του Source2Viewer σε ίντσες του παιχνιδιού, και από εκεί στο πλαίσιο του προβολέα, μια
περιστροφή με ορίζουσα 1), ότι τα clip και ο ουρανός αφαιρούνται ανεξάρτητα από τα πεζά-κεφαλαία και ότι οι επιφάνειες παίρνουν τα ονόματά τους, τον διαχωρισμό εδάφους/κατασκευής κατά κάθετο, και ένα `.glb` που γράφεται και διαβάζεται ξανά.

### Ο έλεγχος του δαπέδου σε πραγματικό χάρτη {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Όταν και οι δύο μεταβλητές είναι ορισμένες, τρέχει και το `test_players_stand_on_the_exported_floor`: μετατρέπει το demo,
εξάγει τον χάρτη του από το εγκατεστημένο παιχνίδι και ελέγχει ότι τουλάχιστον το 98 % από 300 τυχαία δείγματα
θέσης έχουν έδαφος από κάτω τους, με μέση υψομετρική διαφορά από το έδαφος μικρότερη από 5 μονάδες
([Εξαγωγή χάρτη](map-export.md#the-check-that-the-frame-is-right)).

## Συμβάσεις του κώδικα {#conventions-of-the-code}

- Οι χρόνοι μέσα στο `match.py` είναι δευτερόλεπτα αγώνα, εκτός από το `time` ενός φυτέματος, που είναι δευτερόλεπτα
  μέσα στον γύρο του όπως το γράφει το έγγραφο αγώνα· τα tick γίνονται δευτερόλεπτα μόνο μέσω του `_Part.at`.
- Οι πλευρές είναι συμβολοσειρές `T` / `CT` παντού, εκτός από τα ακατέργαστα δεδομένα του αναλυτή (`team_num` 2 / 3).
- Μια νέα στήλη του πίνακα μπαίνει στο `ROW_COLUMNS` (και στο `NUMERIC`, αν είναι αριθμητική) στο `match.py`· το
  `output.table` διαλέγει τον τύπο Parquet της από τα σύνολα `INT16`, `INT32`, `FLOAT64` και τις σημαίες 0/1, αλλιώς
  float32.
- Για να αλλάξει τι κάνει ο προβολέας με μια στήλη, αλλάζει το `HINTS` στο `output.py`.

## Άδεια χρήσης {#licence}

MIT. Τα πακέτα τρίτων και όσα επιβάλλουν τα παιχνίδια: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Τα demo και οι χάρτες δεν είναι ποτέ μέρος του αποθετηρίου· το `.gitignore` του κρατά έξω τα `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` και παρόμοια, ανά τύπο.
