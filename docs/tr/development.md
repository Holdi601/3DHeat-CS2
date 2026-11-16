---
title: Geliştirme
nav_order: 15
lang: "tr"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Geliştirme {#development}

## Yerleşim {#layout}

| Yol | Ne |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: önce sürüm kontrolü, sonra komut satırı |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | komutlar ve seçenekler; demo dosyalarını maçlara gruplamak; işçi havuzu |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | tek bir demo dosyası demoparser2 ile bir `RawPart`'a - [Demo okuma](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | parçalar, zincirler, saat, raundlar, takımlar, satırlar, öldürmeler, hasar, körleşmeler - [Maç oluşturma](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | raund özetleri, skor tablosu, maç belgesi belgesi, metin skor tablosu - [İstatistikler](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | `heat3d` ipuçlarıyla Parquet tablosu ve JSON - [Isı haritası tablosu](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | CS2'yi ve Source2Viewer'ı bulmak, çarpışma ağını görüntüleyicinin çerçevesine çevirmek - [Harita dışa aktarımı](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | küçük bir glTF ikili okuyucu ve yazıcı (numpy dışında bağımlılık yok) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | sürüm kontrolü ve güncelleyici - [Güncellemeler](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testler ve sentetik demo |
| `VERSION` | sürüm, tek satır |

Veri akışı:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Python'dan kullanmak {#using-it-from-python}

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

`Match.kills`, `Match.damage` ve `Match.blinds`, çıktıların taşıdığından daha fazlasını içeren pandas
DataFrame'lerdir - öldürme başına saldırgan ve kurban konumları ve yerleri, vuruş başına `utility` - kendi
analizleriniz için.

## Testler {#tests}

```bash
python -m pytest
```

`pytest.ini`, `tests/` klasörünü sessizce çalıştırır. Testler bir demo, oyun veya Source2Viewer gerektirmez:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) bir demoyu elle
oluşturur, demoparser2'nin vereceği gibi - iki raund, her tarafta iki oyuncu (Alpha takımından `ace`, `ash`;
Bravo'dan `bob`, `ben`) - her cevabın bilindiği kadar küçük:

- 1. raund, T'lerin eleme ile kazanması: ace, bob'u kafa vuruşuyla öldürür (açılış), ben, ace'i 1,9 s sonra
  öldürür (bir takas: bob'un ölümü takas edildi), ash, bundan 3,1 s sonra ben'i öldürür - birine karşı tek
  başına, bir clutch kazanıldı.
- 2. raund, T'lerin bombayla kazanması: ash A'ya bomba kurar, kimse ölmez, bomba patlar.

`fixtures.halves`, boş raundlardan oluşan daha uzun bir maç kurar; takımlar ilk taraflarında veya yer
değiştirmiş olarak, oyunun uzatma sayısıyla veya onsuz, yarı uzunluğu ve tabanca raundları için.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) bunun
üzerinde şunları kontrol eder: her raundun kazananı, nedeni, skoru ve tarafları; maç saati ile başlayan
saat; ekonomi ve kurulum (raund içindeki zamanı, yeri, bombanın patlaması); bir kurulumun sitesinin her
zaman bir harf veya boş olması, asla bir varlık numarası olmaması; karara bağlanan ama kazananı olmayan
bir berabere; yer değiştirmeden tabanca raundları, uzatma dışarıda bırakılarak ve yer değiştirme olmadan
yalnızca 1. raund; klan adı olmayan takımlar (`Started T` / `Started CT`); açılışlar, takaslar ve
bayraklar; intihar olan ama takım arkadaşı öldürmesi olmayan bir öldürme ve açılışın ilk düşman
öldürmesine geçmesi; tablo ve maç belgesinde `noscope` ve `attackerBlind`; hasarın kaybedilen can olarak
(40 canlı birine 137'lik bir vuruştan 60, sonra 40); skor tablosu sayıları ve KAST; clutch'lar; metin skor
tablosu; tablonun olayları ve nerede oldukları (kendi yeri olmayan bir patlama, fırlatanın yeri
`throwerPlace`'te; patlamanın kurulum yapan takıma ait olması); konumların canlı, etiketli olduğu ve birim
bakış vektörleri olduğu; yazılan dosyanın ipuçlarını taşıdığı; parçaların adları ne olursa olsun sıraya
konduğu; yeniden başlatılmış bir sunucu saatinin hâlâ devam ettiği; ve geri yüklenen bir raundun çift
satırlarının, devam eden olana çözüldüğü.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) klasörlerdeki
demoların `.dem` harf durumundan bağımsız bulunduğunu ve bir maçın yalnızca hem tablosu hem maç belgesi
varsa yazılmış sayıldığını kontrol eder.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
çerçeve dönüşümlerini kontrol eder (Source2Viewer'ın metrelerinden oyunun inçlerine, sonra görüntüleyicinin
çerçevesine; determinantı 1 olan bir döndürme), klip ve gökyüzünün harf durumundan bağımsız ve adları
geçen yüzeyler dışarıda bırakıldığını, zemin/yapı ayrımının normale göre yapıldığını ve bir `.glb`'nin
yazılıp geri okunduğunu.

### Gerçek bir haritada zemin kontrolü {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

İki değişken de ayarlıyken `test_players_stand_on_the_exported_floor` da çalışır: demoyu çevirir, haritasını
yüklü oyundan dışa aktarır ve rastgele 300 konum örneğinin en az %98'inin altında zemin olduğunu ve zeminin
üstündeki medyan yüksekliğin 5 birimin altında olduğunu kontrol eder
([Harita dışa aktarımı](map-export.md#the-check-that-the-frame-is-right)).

## Kodun kuralları {#conventions-of-the-code}

- `match.py` içindeki zamanlar maç saniyeleridir; bir kurulumun `time` değeri hariç, o da maç belgesinin
  yazdığı gibi, raund içindeki saniyedir; tikler yalnızca `_Part.at` üzerinden saniyeye dönüşür.
- Taraflar, ham çözümleyici verisi dışında her yerde `T` / `CT` dizgileridir (`team_num` 2 / 3).
- Yeni bir tablo sütunu `match.py` içindeki `ROW_COLUMNS`'a (sayısalsa `NUMERIC`'e) girer; `output.table`,
  Parquet türünü `INT16`, `INT32`, `FLOAT64` ve 0/1 bayrakları kümelerinden seçer, geri kalanı float32'dir.
- Görüntüleyicinin bir sütunla ne yapacağını değiştirmek, `output.py` içindeki `HINTS`'i değiştirmek demektir.

## Lisans {#licence}

MIT. Üçüncü taraf paketler:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demolar ve haritalar deponun parçası değildir; `.gitignore` dosyası `*.dem`, `*.parquet`, `*.match.json`,
`*.glb` ve benzerlerini türüne göre dışarıda tutar.
