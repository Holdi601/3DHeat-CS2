---
title: Kurulum
nav_order: 3
lang: "tr"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Kurulum {#installing}

Komut satırına yeni misiniz? Önce [Başlamadan önce](before-you-start.md) sayfasını okuyun.

3DHeat CS2, kendi klasöründen çalıştırılan bir Python paketidir. Derlenecek bir şey yok ve bir kurucu yok;
Python, dört paket (testler için ayrıca pytest) gerekir ve - yalnızca harita dışa aktarımı için - kurulu
Counter-Strike 2 ile Source2Viewer'ın komut satırı sürümü.

## Kodu almak {#getting-the-code}

[sürümler sayfasından](https://github.com/Holdi601/3DHeat-CS2/releases) bir sürüm arşivi indirip açın ya da
Git'iniz varsa depoyu klonlayın:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

İki tür kopya da kendini güncelleyebilir (bkz. [Güncellemeler](updates.md)). Kurulu sürüm, `VERSION`
dosyasındaki tek satırdır.

Her komutu bu klasörden çalıştırın: `python -m heat3d_cs2` paketi, geçerli dizinde olduğu için bulur. Paket
`site-packages` içine kurulmaz.

## Python ve paketler {#python-and-the-packages}

Python 3.10 veya üstü. Sanal bir ortam, paketleri başka şeylerden ayrı tutar. Windows'ta (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

PowerShell betiği çalıştırmayı reddederse, önce
`Set-ExecutionPolicy -Scope Process RemoteSigned` komutunu çalıştırın (yalnızca o pencerede geçerlidir).
Linux veya macOS'ta:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`python -m heat3d_cs2 --help` `usage: heat3d_cs2 ...` yazdırdığında çalışıyor demektir.

`requirements.txt`:

| Paket | En düşük | Ne için kullanılır | Lisans |
|---|---|---|---|
| `demoparser2` | 0.42 | `.dem` dosyalarını okumak (tik başına oyuncular, oyun olayları) | MIT |
| `pyarrow` | 15 | Parquet tablosunu yazmak | Apache-2.0 |
| `pandas` | 2.0 | aradaki tablolar | BSD-3-Clause |
| `numpy` | 1.24 | onlar üzerinde aritmetik | BSD-3-Clause |
| `pytest` | 8.0 | yalnızca testler | MIT |

`demos` ve `scoreboard` komutlarının başka bir şeye ihtiyacı yoktur.

## Harita dışa aktarımı için: Counter-Strike 2 ve Source2Viewer'ın CLI'si {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` haritayı kurulu oyundan okur ve bunu **Source2Viewer'ın komut satırıyla** çözer;
bu, [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) projesinden ayrı bir
programdır (MIT lisanslı). Paketle birlikte gelmez ve pip ile kurulamaz.

1. Sisteminiz için **CLI** sürümünü [ValveResourceFormat sürümleri sayfasından](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   indirin ve istediğiniz yere açın.
2. Bulunabilir hâle getirin; üç yoldan biriyle. Şu sırayla denenirler:
   1. komut satırında `--source2viewer <çalıştırılabilir dosyanın yolu>`;
   2. çalıştırılabilir dosyanın yoluna ayarlanmış `HEAT3D_SOURCE2VIEWER` ortam değişkeni;
   3. `PATH` üzerinde `Source2Viewer-CLI` veya `Source2Viewer-CLI.exe` adında bir çalıştırılabilir dosya.

   Bir aday yalnızca yolu varsa kullanılır. Hiçbiri bulunamazsa komut şöyle durur:
   `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Değişkeni ayarlamak, örneğin:

```bash
# Windows (PowerShell), geçerli oturum için
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### CS2'nin nerede aranacağı {#where-cs2-is-looked-for}

Harita, oyunun klasörü altındaki bir `.vpk` arşividir:
`<Steam kütüphanesi>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Steam kütüphaneleri şu köklerden ve her kökün `config\libraryfolders.vdf` dosyasında listelenen her
`"path"` değerinden bulunur:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Steam başka bir yerdeyse, CS2 klasörünün kendisini `--game` ile verin (`game\csgo` içeren klasör) ya da harita
adı yerine `.vpk` yolunu verin. Bkz. [Harita dışa aktarımı](map-export.md).

## Kurulumu kontrol etmek {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testler kodda oluşturulan sentetik bir demo üzerinde çalışır ve demo, oyun veya Source2Viewer gerektirmez
(bkz. [Geliştirme](development.md)).

`python -m heat3d_cs2` her başlatıldığında, en fazla altı saatte bir, daha yeni bir sürüm olup olmadığına
bakılır; bunu kapatmak için `HEAT3D_NO_UPDATE=1` ayarlayın (bkz. [Güncellemeler](updates.md)).
