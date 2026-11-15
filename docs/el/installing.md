---
title: "Εγκατάσταση"
nav_order: 3
lang: "el"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Εγκατάσταση {#installing}

Δεν έχετε ξαναδουλέψει με τη γραμμή εντολών; Διαβάστε πρώτα το [Πριν ξεκινήσετε](before-you-start.md).

Το 3DHeat CS2 είναι ένα πακέτο Python που τρέχει από τον δικό του φάκελο. Δεν χρειάζεται να χτιστεί και δεν έχει
εγκαταστάτη· θέλει Python, τέσσερα πακέτα (συν το pytest για τις δοκιμές) και, μόνο για την εξαγωγή χάρτη, το
Counter-Strike 2 εγκατεστημένο και την έκδοση γραμμής εντολών του Source2Viewer.

## Λήψη του κώδικα {#getting-the-code}

Κατεβάστε ένα αρχείο έκδοσης από τη [σελίδα εκδόσεων](https://github.com/Holdi601/3DHeat-CS2/releases) και
αποσυμπιέστε το, ή, αν έχετε Git, κλωνοποιήστε το αποθετήριο:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Και τα δύο είδη αντιγράφου μπορούν να ενημερώνονται μόνα τους (βλ. [Ενημερώσεις](updates.md)). Η εγκατεστημένη
έκδοση είναι η μία γραμμή του αρχείου `VERSION`.

Τρέχετε κάθε εντολή από αυτόν τον φάκελο: το `python -m heat3d_cs2` βρίσκει το πακέτο επειδή είναι στον τρέχοντα
φάκελο. Το πακέτο δεν εγκαθίσταται στο `site-packages`.

## Python και τα πακέτα {#python-and-the-packages}

Python 3.10 ή νεότερη. Ένα εικονικό περιβάλλον κρατά τα πακέτα χωριστά από τα υπόλοιπα. Στα Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Αν το PowerShell αρνηθεί να τρέξει το σενάριο, τρέξτε πρώτα
`Set-ExecutionPolicy -Scope Process RemoteSigned` (ισχύει μόνο για εκείνο το παράθυρο). Στο Linux ή στο macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Λειτουργεί όταν το `python -m heat3d_cs2 --help` τυπώνει `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Πακέτο | Ελάχιστη έκδοση | Χρήση | Άδεια |
|---|---|---|---|
| `demoparser2` | 0.42 | διαβάζει αρχεία `.dem` (παίκτες ανά tick, γεγονότα παιχνιδιού) | MIT |
| `pyarrow` | 15 | γράφει τον πίνακα Parquet | Apache-2.0 |
| `pandas` | 2.0 | οι ενδιάμεσοι πίνακες | BSD-3-Clause |
| `numpy` | 1.24 | αριθμητικές πράξεις σ' αυτούς | BSD-3-Clause |
| `pytest` | 8.0 | μόνο για τις δοκιμές | MIT |

Οι εντολές `demos` και `scoreboard` δεν χρειάζονται τίποτα άλλο.

## Για την εξαγωγή χάρτη: Counter-Strike 2 και η γραμμή εντολών του Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewer-s-cli}

Το `python -m heat3d_cs2 map` διαβάζει τον χάρτη από το παιχνίδι που έχετε εγκατεστημένο, και τον αποκωδικοποιεί με
τη **γραμμή εντολών του Source2Viewer**, ένα χωριστό πρόγραμμα από το έργο
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (άδεια MIT). Δεν συνοδεύεται από το
πακέτο και δεν εγκαθίσταται με το pip.

1. Κατεβάστε την έκδοση **CLI** για το σύστημά σας από
   [τις εκδόσεις του ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   και αποσυμπιέστε την όπου θέλετε.
2. Κάντε την εντοπίσιμη με έναν από τους τρεις τρόπους. Δοκιμάζονται με αυτή τη σειρά:
   1. `--source2viewer <διαδρομή προς το εκτελέσιμο>` στη γραμμή εντολών·
   2. η μεταβλητή περιβάλλοντος `HEAT3D_SOURCE2VIEWER` με τη διαδρομή του εκτελέσιμου·
   3. ένα εκτελέσιμο με όνομα `Source2Viewer-CLI` ή `Source2Viewer-CLI.exe` στο `PATH`.

   Ένας υποψήφιος χρησιμοποιείται μόνο αν η διαδρομή του υπάρχει. Αν δεν βρεθεί κανένας, η εντολή σταματά με το μήνυμα
   `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Ορισμός της μεταβλητής, για παράδειγμα:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Πού ψάχνεται το CS2 {#where-cs2-is-looked-for}

Ο χάρτης είναι ένα αρχείο `.vpk` μέσα στον φάκελο του παιχνιδιού:
`<βιβλιοθήκη Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Οι βιβλιοθήκες Steam βρίσκονται από αυτές τις ρίζες, και από κάθε `"path"` που αναφέρεται στο
`config\libraryfolders.vdf` κάθε ρίζας:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Όταν το Steam είναι αλλού, δώστε τον ίδιο τον φάκελο του CS2 με `--game` (τον φάκελο που περιέχει το `game\csgo`), ή
δώστε τη διαδρομή του `.vpk` στη θέση του ονόματος του χάρτη. Βλ. [Εξαγωγή χάρτη](map-export.md).

## Έλεγχος της εγκατάστασης {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Οι δοκιμές τρέχουν σε ένα συνθετικό demo που φτιάχνεται μέσα στον κώδικα, και δεν χρειάζονται demo, παιχνίδι ή
Source2Viewer (βλ. [Ανάπτυξη](development.md)).

Σε κάθε εκκίνηση του `python -m heat3d_cs2` ελέγχεται πρώτα, το πολύ κάθε έξι ώρες, αν έχει βγει νεότερη έκδοση·
ορίστε `HEAT3D_NO_UPDATE=1` για να το απενεργοποιήσετε (βλ. [Ενημερώσεις](updates.md)).
