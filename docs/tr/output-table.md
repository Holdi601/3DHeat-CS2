---
title: Isı haritası tablosu
nav_order: 8
lang: "tr"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Isı haritası tablosu (`<match>.parquet`) {#the-heatmap-table-parquet}

Maç başına bir Parquet dosyası: her canlı oyuncunun örneklenmiş konumu ve olayların olduğu her yer, her biri bir satır -
3DHeat görüntüleyicisinin ısı haritası olarak okuduğu uzun bir tablo, başka her şey için sıradan bir tablo. Kod:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) (dosya),
[`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(satırlar; bkz. [Maç oluşturma](building-matches.md)).

Dosya, 256.000 satırlık satır gruplarında Snappy sıkıştırmasıyla yazılır. Satırlar önce `time`'a, sonra `event`'e göre
sıralanır. Yalnızca bir raundun içindeki satırlar (raundun dondurma süresinin bitişinden bir sonraki raundun başlangıcına
kadar) tablodadır.

Testlerdeki sentetik demoda, ilk raundun olay satırları:

![tablonun olay satırları](../assets/img/table-rows.svg)

Bir `.3dheat` kapsayıcısında tablo, `table` rolündeki öğedir ([Her maç için tek dosya](output-container.md)).

## Sütunlar {#columns}

Sütunlar her zaman bu sırayla. Metin sütunları sözlük kodlu dizgilerdir (`dictionary<int32, string>`) ve asla boş
(null) değildir: "değer yok" boş bir dizgidir. Sayısal sütunlar, bir satırın değeri olmadığında null'dır.

| Sütun | Tür | Ne |
|---|---|---|
| `match` | dizge | maç adı (`alpha-vs-bravo-m1`, ya da ikinci bir zincir için `...-b`) |
| `map` | dizge | harita, demo başlığından (`de_x`) |
| `round` | int16 | raund numarası, 1'den başlar |
| `roundId` | dizge | `<match> #NN`, raund numarası iki basamaklı (`alpha-vs-bravo-m1 #07`): maçlar arasında benzersiz, görüntüleyicinin oturumu |
| `phase` | dizge | `freeze`, raundun dondurma süresinde (önceki raundun bitişinden itibaren), `live`, raund karara bağlanana kadar, `after`, kazananlar avlanırken ve kaybedenler kurtarırken |
| `time` | float64 | maç başladığından beri saniye (ilk dosyanın canlı başlangıcı), dosyaları boyunca tek bir saatte |
| `roundTime` | float32 | bu raundun dondurma süresi bittikten beri saniye; dondurma süresinde negatif |
| `event` | dizge | satırın ne olduğu - [Olaylar](#events) |
| `player` | dizge | oyuncunun adı (her olay için hangi oyuncu olduğu aşağıda söylenir) |
| `steamid` | dizge | oyuncunun Steam kimliği (64 bit, metin olarak) |
| `side` | dizge | bu raundaki `T` veya `CT`; oyuncu hiçbir tarafta değilse boş |
| `team` | dizge | oyuncunun takım adı (veya `Started T` / `Started CT`); `explode` için kurulum yapan takım |
| `x`, `y`, `z` | float32 | oyunun kendi koordinatlarında konum: inç (oyun birimleri), **Z yukarı**, sağ el kuralı |
| `dirX`, `dirY`, `dirZ` | float32 | oyuncunun baktığı yön, aynı çerçevede bir birim vektör; yalnızca konumlar |
| `health` | int16 | 0-100; konumlarda, `hurt`'te ise vuruştan sonra kalan |
| `armor` | int16 | 0-100; konumlarda, `hurt`'te ise vuruştan sonra kalan |
| `money` | int32 | oyuncunun parası; yalnızca konumlar |
| `equipment` | int32 | oyuncunun taşıdıklarının değeri; yalnızca konumlar |
| `weapon` | dizge | silah, oyunun adıyla (`AK-47`, `M4A1-S`, her bıçak kaplaması için `Knife`) |
| `place` | dizge | satırın konumundaki haritanın kendi yer adı (`BombsiteA`, `CTSpawn`); bomba patlamalarında boş: demo bir bombanın nerede patladığı için yer adı vermez |
| `throwerPlace` | dizge | bomba patladığında fırlatanın yer adı; yalnızca bomba patlamaları |
| `other` | dizge | bir öldürme, ölüm, vuruş veya flaşın diğer oyuncusu |
| `damage` | float32 | kaybedilen can; yalnızca `hurt` |
| `duration` | float32 | körleşme saniyesi; yalnızca `blind` |
| `headshot` | int8 | 0/1; yalnızca `kill` ve `death` |
| `opening` | int8 | 0/1, raundun bir düşmanın ilk öldürmesi; yalnızca `kill` ve `death` |
| `traded` | int8 | 0/1. Bir `kill` için: takas öldürmesiydi. Bir `death` için: 5 s içinde intikamı alındı. Yalnızca `kill` ve `death`. |
| `noscope` | int8 | 0/1, öldürme dürbünlü bir silahla, dürbünsüz ateşlenerek yapıldı (olayın `noscope`'u); yalnızca `kill` ve `death` |
| `attackerBlind` | int8 | 0/1, katil öldürdüğünde flaşlanmıştı (olayın `attackerblind`'ı); yalnızca `kill` ve `death` |
| `won` | int8 | 0/1, bu satırın tarafı raundu kazandı mı; `side` boşsa null |
| `matchWon` | int8 | 0/1, bu satırın takımı maçı kazandı mı; `team` boşsa veya kayıt bitişi göstermiyorsa null (bkz. maç belgesindeki `winner`) |
| `roundEndReason` | dizge | satırın raundunun nasıl bittiği: `elimination`, `bomb` (bomba patladı), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | dizge | satırın tarafının o raunttaki alımı: `pistol`, `eco`, `force`, `full` |
| `detail` | dizge | diğer sütunların taşımadığı olayın her alanı, JSON nesnesi olarak (oyunun kendi adlarıyla): bir atışın mermileri (`fire_bullets`: köken, açılar, isabetsizlik, yayılma, geri tepme indeksi, tohum...), bir ölümün `dominated`, `revenge`, `attackerinair`, `wipe`..., bir eşyanın `defindex`'i, bir ayak sesinin hiçbir şeyi |
| `text` | dizge | bir sohbet satırı; yalnızca `chat` |
| `entity` | int32 | bombanın varlığı: bir `throw`'un uçuşu (`grenade` satırları), patlaması ve körlediği oyuncular aynısını paylaşır |
| `hitgroup` | dizge | mermi nerede isabet etti (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | kaybedilen zırh; yalnızca `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | mermi vücudun neresine isabet etti, kurbanın çerçevesinde metre cinsinden (x ileri, y ayaklardan yukarı, z sağ): atışın ışını (`fire_bullets`, yoksa saldırganın göz ve bakışı), kurbanın durduğu ve eğildiği gibi poz verilmiş bir vücuda izlenir, `hitgroup`'un adını verdiği parçaya; yalnızca `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | atışın yönü aynı çerçevede; `hitMiss` ışının adı verilen parçanın ne kadar yanından geçtiği (m) (0: içinden); `hitFrom` `bullet` veya `aim` |
| `penetrated` | int16 | öldürücü merminin geçtiği duvar sayısı; `kill` ve `death` |
| `throughSmoke` | int8 | 0/1, duman içinden öldürüldü; `kill` ve `death` |
| `distance` | float32 | öldürmenin mesafesi, oyunun saydığı gibi (metre); `kill` ve `death` |
| `assister` | dizge | kim asist yaptı; `kill` ve `death` |
| `flash`, `flashAlpha` | float32 | kalan flaş saniyesi ve ne kadar beyaz olduğu; konumlar |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; konumlar |
| `zoom`, `duck`, `moveType` | | dürbünün yakınlaştırma seviyesi, ne kadar eğildiği (0-1), oyunun hareket türü; konumlar |
| `spottedBy` | dizge | bu oyuncuyu gören düşmanların Steam kimlikleri, `\|` ile ayrılmış; konumlar |
| `inventory` | dizge | oyuncunun taşıdığı her şey, `\|` ile ayrılmış; konumlar |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | elde tutulan silahın şarjörü ve yedeği; mevcut patlamadaki atışlar; konumlar |
| `punchPitch`, `punchYaw` | float32 | nişan geri tepmesi, derece; konumlar |
| `ping` | int16 | milisaniye; konumlar |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | maç şimdiye kadar için oyunun kendi skor tablosu sayıları; konumlar |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | bu raundda ve maçta harcanan para; raund başladığındaki ekipman değeri; konumlar |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, oyuncunun satırın zamanındaki durumu, olaylar dahil: kask, etkisizleştirme kiti, herhangi bir zırh, dürbünlü (oyuncunun son konum örneğinden satıra kadar), flaşlanmış (oyuncuyu vuran bir `blind` içinde); bir oyuncuyu adlandıran her satır |
| `state_utility` | int16 | o andaki taşınan bombalar (`inventory`'den); bir oyuncuyu adlandıran her satır |
| `state_weapon` | dizge | o anda elde tutulan silah (bir `death`'te kurbanın kendi silahı, `weapon` katilinki iken); bir oyuncuyu adlandıran her satır |
| `earn_round_cs2` | int16 | raundun ödediği: `round_end`'de kazanma ödülü veya kaybetme bonusu (kurucu tarafın bonusuyla birlikte), `plant` ve `defuse`'ta oyuncunun 300'ü |

## Olaylar {#events}

Hangi oyuncunun bir satırı adlandırdığı, nerede durduğu ve hangi sütunları doldurduğu.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason` ve `buy` her satırda
doldurulur (maçın kazananı biliniyorsa `matchWon` da); `inventory`, `money`, `equipment` ve `state_*` sütunları bir oyuncuyu
adlandıran her satırda (olaylar bunları oyuncunun son konum örneğinden alır) doldurulur.

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Ayrıca doldurulanlar |
|---|---|---|---|
| `position` | oyuncu | oyuncu (ayaklar) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (elde), `place` ve oyuncunun tüm durumu (`flash`'tan itibaren sütunlar) - dondurma süresinde de |
| `kill` | katil | katilin durduğu yer | `other` (kurban), `weapon`, `headshot`, `opening`, `traded` (takas öldürmesi), `noscope`, `attackerBlind`, `place` |
| `death` | kurban | kurbanın düştüğü yer | `other` (katil; dünya için boş), `weapon`, `headshot`, `opening`, `traded` (intikamı alındı), `noscope`, `attackerBlind`, `place` |
| `hurt` | kurban | kurbanın vurulduğu yer | `other` (saldırgan), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - takım arkadaşlarının ve dünyanın vuruşları da |
| `shot` | nişancı | atışın yapıldığı yer | `weapon`, `place`, `detail` (oyunun mermiler hakkındaki açıklaması) |
| `slash` | oyuncu | bıçağın sallandığı yer | `weapon` = `Knife` |
| `grenade` | fırlatan | uçuştaki bomba, oyuncuların örneklenmesinde ve durduğu yerde | `weapon` (bomba), `entity` |
| `throw` | fırlatan | bombanın atıldığı yer | `weapon` (bomba), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | fırlatan | patladığı yer | `weapon`, `throwerPlace` (o andaki fırlatanın yeri); `place` boş kalır |
| `blind` | flaşlanan oyuncu | durdukları yer | `other` (flaşı atan), `duration`, `weapon` = `Flashbang`, `entity`, `place` - flaşlanan takım arkadaşları da |
| `plant` | kurucu | kurduğu yer | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | etkisizleştiren | etkisizleştirdiği yer | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | raundu oynayan her oyuncu | oyuncunun en son durduğu yer | `won`, `earn_round_cs2` (raundun onlara ödediği: kurallar izin veriyorsa tarafın parasının bir sonraki dondurma süresine yükselişi, yoksa kuralların kendi değeri), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | kurucu (Steam kimliğiyle), taraf `T`, kurucu takım | kurulumun konumu | `weapon` = `C4 Explosive`, `place` (kurucunun kurulum anındaki yeri: bombanın durduğu yer); zamanı bombanın patladığı andır |
| `chat` | gönderen | nerede olduğu | `text` |
| oyuncuyla ilgili diğer her oyun olayı, oyunun adıyla: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | oyuncu | nerede olduğu (bir bombanın olayları: bombanın nerede olduğu) | `weapon` (bir eşyanın), `entity`, `detail` (olayın her alanı) |

Neyin içinde olduğu ve neyin olmadığı:

- **position** satırları, dondurma süresi ve ısınma dışında, bir taraftaki yaşayan oyunculardır, her `--every` tikte
  (varsayılan olarak saniyede sekiz).
- **kill** satırları yalnızca bir düşman tarafından yapılan öldürmelerdir - takım arkadaşı öldürmesi, intihar veya dünyaya
  ölüm yok. **death** satırları her ölümdür, bunlar dahil.
- **explode** satırları, demonun `bomb_exploded` olayına göre patlayan her kurulu bombadır: sonrası aşamasında da, T'ler zaten
  eleme ile kazanmışken. Bu olayı olmayan bir demo, bombanın kazandığı her raund için, raundun sonunda bir tane alır.
- **hurt** ve **blind** satırları yalnızca düşmanlar arasındadır.
- **shot** bıçakları ve C4'ü dışarıda bırakır; bombalar **throw** satırlarıdır.
- **molotov**, molotovları ve incendiary'leri kapsar (ateşin başlaması).
- Takım arkadaşlarının hasarı, takım arkadaşlarının ve izleyicilerin flaşları, dondurma süresi olayları ve raundlar arasındaki
  her şey tabloda değildir.

Testlerdeki sentetik demodan çalışılmış bir örnek (atılan bir duman, bir kafa vuruşuyla açılış öldürmesi, takaslar):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

bob'un ölümü, ben'in 1,9 s sonra ace'i öldürmesiyle intikamı alınır (bob'un `death` satırı: traded 1; ben'in `kill` satırı: bir
takas öldürmesi, traded 1); bob'a yapılan ikinci vuruş 40 cana karşı 137 hasardı, bu yüzden 40 sayılır.

## `heat3d` alt bilgi ipuçları {#the-heat3d-footer-hints}

Dosyanın Parquet alt bilgisi (şema anahtar/değer üst verisi), **`heat3d`** anahtarı altında okuma talimatlarını taşır; bir JSON nesnesi:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "matchWon", "roundEndReason", "buy", "opening", "team", ...]
  }
}
```

| Giriş | Ne söyler |
|---|---|
| `version`, `kind` | ipuçlarının sürümü (1) ve bunları yazanın türü (`cs2-demo`) |
| `axes.up` | dosyanın Z'si yukarıdır |
| `axes.flipY` | dosyanın Y'sini negatif yap (aşağıya bakın) |
| `axes.scale` | 1: konumlar olduğu gibi, oyun birimlerinde kullanılır |
| `entity.size` | bir oyuncu **32 birim** geniştir - CS2 oyuncusunun genişliği - bir kutu tekrarının çizdiği boyut |
| `columns.x` / `y` / `z` | konum sütunları |
| `columns.time`, `timeUnit` | `time`, saniye cinsinden |
| `columns.personId` | oyuncu kişidir |
| `columns.teamId` | taraf gruptur (yani gruplara renk veren T ve CT'dir, takım adları değil) |
| `columns.sessionId` | her raund (`roundId`) bir oturumdur |
| `columns.lookMode` ve `dirX`-`dirZ` | bakış yönü bu sütunlarda bir vektördür |
| `columns.extra` | filtre olarak tutulacak sütunlar, kullanışlılık sırasıyla |

Anahtarı bilen bir görüntüleyici dosyayı hiçbir şey ayarlamadan açar. Başka her şey bunu yok sayar. Kendiniz okumak için:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Eksenler ve birimler {#axes-and-units}

Koordinatlar oyunun kendi koordinatlarıdır: **inç** (bir oyun birimi; bir oyuncu ayaktayken 72 birim, 32 birim genişliğinde),
**Z yukarı** ve sağ el kuralı.

Dünyası Y-yukarı olan bir görüntüleyici, oyunun (x, y, z) değerini **(x, z, -y)** olarak çizmelidir - Z yükseklik olur ve Y
negatif yapılır. Bu bir döndürmedir, ayna değil. Sol el kuralıyla Z-yukarı bir dünyanın çizdiği gibi (x, z, y) olarak çizilirse,
her harita ayna görüntüsü olur, A sitesi yanlış tarafta; `flipY: true`, ipuçlarının bunu önlemek için söylediğidir.
[Harita dışa aktarımı](map-export.md) geometrisini zaten aynı birimlerde (x, z, -y) çerçevesinde yazar, bu yüzden hiçbir ayar
yapmadan tablonun altına oturur.

Görüntüleyicideki mesafeler metre olarak etiketlenir; ölçek 1 olduğunda oyun birimleridir. Metreye çevirmek için 0.0254 ile çarpın.

## Boyut {#size}

Konumlar baskındır: varsayılan `--every 8` ile canlı oynanışta saniyede sekiz kez, on oyuncu x 8 örnek kadar; ölü oyuncular ve
dondurma süresi için daha az. `--every` değerini yarıya indirmek konumları ikiye katlar; olaylar etkilenmez.
