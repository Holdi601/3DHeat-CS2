---
title: "Ένα αρχείο ανά αγώνα"
nav_order: 10
lang: "el"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Ένα αρχείο ανά αγώνα (`<match>.3dheat`) {#one-file-a-match-3dheat}

Από προεπιλογή το `demos` πακετάρει κάθε αγώνα σε ένα αρχείο, `out/<map>/<match>.3dheat`: τον πίνακα χάρτη θερμότητας,
το έγγραφο αγώνα και τα τέσσερα βοηθητικά αρχεία μαζί - ένας αγώνας, ένα αρχείο, για να το αντιγράψετε, να το
κρατήσετε ή να το μοιραστείτε. Είναι η μορφή κοντέινερ του προβολέα του 3DHeat, που περιγράφεται στην τεκμηρίωση του
προβολέα:
[Ένα αρχείο ανά αγώνα (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([πηγή](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Κώδικας: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Βήμα προς βήμα {#step-by-step}

1. Μετατρέψτε όπως συνήθως· δεν χρειάζεται να ρυθμίσετε τίποτα:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Κάθε αγώνας είναι ένα αρχείο μέσα στον φάκελο του χάρτη του:

   ![demos σε συνθετικό demo](../assets/img/demos-run.svg)

3. Ανοίξτε το στον προβολέα (καρτέλα **Χάρτης θερμότητας** ή **Αγώνας**), ή διαβάστε το μόνοι σας: είναι ένα συνηθισμένο
   αρχείο ZIP.

   ![μέσα σε ένα κοντέινερ .3dheat](../assets/img/container-members.svg)

Αν θέλετε να κρατήσετε τα ξεχωριστά αρχεία, για εργαλεία που θέλουν ένα αρχείο Parquet στον δίσκο, προσθέστε
`--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Τι περιέχει {#what-is-inside}

Ένα ZIP του οποίου το πρώτο μέλος είναι το `manifest.json`, και μετά τα υπόλοιπα μέλη. Τα μέλη Parquet είναι
*αποθηκευμένα* (το Parquet είναι ήδη συμπιεσμένο, και ένα αποθηκευμένο μέλος είναι ένα εύρος byte που ένας αναγνώστης
μπορεί να χρησιμοποιήσει στη θέση του)· τα μέλη JSON είναι συμπιεσμένα με deflate.

| Ρόλος | Μέλος | Τι είναι |
|---|---|---|
| `table` | `<match>.parquet` | [Ο πίνακας χάρτη θερμότητας](output-table.md) (σχήμα `heat3d-table`) |
| `match` | `<match>.match.json` | [Το έγγραφο αγώνα](output-match-json.md) (σχήμα `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | κάθε γεγονός παιχνιδιού που διαβάζει ο αναλυτής, ολόκληρο |
| `props` | `<match>.props.parquet` | κάθε αλλαγή ιδιότητας που διαβάζει ο αναλυτής |
| `strings` | `<match>.strings.parquet` | κάθε εγγραφή του πίνακα συμβολοσειρών |
| `packets` | `<match>.packets.parquet` | κάθε άλλο καρέ και μήνυμα δικτύου, ολόκληρο |

Το manifest δίνει τη μορφή και την έκδοσή της, το παιχνίδι (`cs2`), την πηγή (`demo`), τον μετατροπέα και την έκδοσή του,
τον αγώνα, τον χάρτη, πότε γράφτηκε, έναν χάρτη `roles` από ρόλο σε μέλος, και για κάθε μέλος τον τύπο μέσου, τη
συμπίεση, το μέγεθος, το SHA-256, τον αριθμό γραμμών και, όπου έχει, το σχήμα του. Στο συνθετικό demo των δοκιμών
(συντομευμένο):

```json
{
  "format": "3dheat",
  "format_version": "1.0",
  "game": "cs2",
  "source": "demo",
  "converter": { "name": "heat3d_cs2", "version": "1.0.2" },
  "match": "alpha-vs-bravo-m1",
  "map": "de_test",
  "roles": {
    "table": "alpha-vs-bravo-m1.parquet",
    "match": "alpha-vs-bravo-m1.match.json",
    "events": "alpha-vs-bravo-m1.events.parquet",
    "packets": "alpha-vs-bravo-m1.packets.parquet",
    "props": "alpha-vs-bravo-m1.props.parquet",
    "strings": "alpha-vs-bravo-m1.strings.parquet"
  },
  "members": [
    {
      "name": "alpha-vs-bravo-m1.parquet",
      "role": "table",
      "media_type": "application/vnd.apache.parquet",
      "compression": "stored",
      "bytes": 38769,
      "sha256": "1b7b7d16...",
      "rows": 2655,
      "schema": { "id": "heat3d-table", "version": "1" }
    }
  ]
}
```

## Ανάγνωση χωρίς τον προβολέα {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

Η εντολή `scoreboard` διαβάζει το έγγραφο αγώνα απευθείας από το κοντέινερ (ή από ένα ξεχωριστό `.match.json`).

## Παράλειψη και ξαναγράψιμο {#skipping-and-rewriting}

Ένα κοντέινερ γράφεται ολόκληρο ή καθόλου, οπότε ένα `.3dheat` κάτω από το `--out` μετράει ως αγώνας που έχει γίνει·
το `--force` το ξαναγράφει. Ένας αγώνας που μετατράπηκε νωρίτερα με `--loose` μετράει επίσης ως γραμμένος.
