---
title: Maç belgesi
nav_order: 9
lang: "tr"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Maç belgesi (`<match>.match.json`) {#the-match-document-matchjson}

Her maç için tablosunun yanında bir JSON belgesi: takımlar, skor, sonucuyla her raund, ekonomi, kurulum, öldürmeler,
clutch'lar ve hayatta kalanlar ve her oyuncunun skor tablosu satırı. 3DHeat görüntüleyicisinin Maç sekmesinin yüklediği
şey budur. Kod: [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) içindeki
`summary()`; sayıların tanımları [İstatistikler](statistics.md) sayfasındadır.

Dosya UTF-8'dir, her girinti bir boşluktur ve ASCII olmayan karakterleri (oyuncu ve takım adları) olduğu gibi tutar.
Zamanlar saniyedir; raundlar için üç, öldürmeler ve kurulum için iki ondalığa yuvarlanmıştır.

## Belge {#the-document}

| Alan | Tür | Ne |
|---|---|---|
| `format` | dizge | her zaman `heat3d-cs2-match` - okuyucunun dosyayı tanıma yolu |
| `version` | sayı | `3`. Sürüm 1 belge, bir kurulumun `time` değerini maç saniyesi olarak verir; 2'den itibaren, bir öldürmeninki gibi raund içindeki saniyedir. 3, `header`'dan itibaren alanları ekler ve dondurma süresini tabloya ekler. |
| `match` | dizge | maç adı, dosyaların adlandırıldığı gibi |
| `map` | dizge | harita (`de_x`) |
| `demos` | dizge[] | yapıldığı demo dosyaları, yalnızca dosya adları, maç sırasında |
| `teams` | dizge[] | görünüş sırasında takım adları (1. raund: önce T tarafı) |
| `score` | nesne | takım adı -> kazanılan raund sayısı: son raundun skoru |
| `winner` | dizge veya null | maçı kazanan takım, kaydın bitişi gösteriyorsa; kaydın erken durduğu, kazanma panosu olmayan bir uzatma veya beraberlik için null |
| `winnerSource` | dizge veya null | `winner`'ın nasıl bilindiği: `winPanel` (oyunun maç kazanma panosu), `surrender` (teslim), `regulation` (normal raundların yarısından fazlası) |
| `rounds` | nesne[] | tamamlanmış her raund, sırayla - [aşağıda](#rounds) |
| `incomplete` | sayı[] | bir demonun sonuyla kesilen ve dışarıda bırakılan raund numaraları |
| `missing` | sayı[] | demoların tuttuğu ilk raundan önceki raund numaraları: kayıt 3. raundda başlıyorsa `[1, 2]` |
| `halfLength` | sayı veya null | normal bir yarıdaki raund sayısı, taraflar ilk kez yer değiştirdiği yerden (24 raundluk formatta `12`); kayıt yer değiştirmeyi göstermiyorsa null |
| `pistolRounds` | sayı[] | `buy`'ın sayıldığı tabanca raundları: 1. raund ve `halfLength` biliniyorsa yarıdan sonraki raund; asla uzatma raundu değil |
| `players` | nesne[] | skor tablosu - [aşağıda](#players) |
| `conventions` | nesne | sayıların arkasındaki tanımlar, [aşağıda](#conventions) |
| `header` | nesne | ilk demonun başlığı, çözümleyicinin verdiği haliyle: sunucu adı, yama sürümü, demo sürümü, harita |
| `profiles` | nesne | Steam kimliği -> maç boyunca bir oyuncu için sabit kalan şeyler: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (en son görülen) |
| `playerInfo` | nesne[] | demoların listelediği her oyuncu, antrenörler ve yayıncılar dahil: Steam kimliği, adı, takım numarası |
| `skins`, `itemDrops` | nesne[] | silah kaplamaları ve eşya düşmeleri, demoda varsa (yayın demolarında yoktur) |
| `chat` | nesne[] | maçtaki her sohbet satırı: zaman, raund, oyuncu, taraf, metin |
| `events` | nesne[] | hiçbir oyuncuyla ilgili olmayan her oyun olayı, zaman sırasıyla, tüm alanlarıyla: raund sesleri ve aşamaları, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (sunucu ayarları değiştikçe), yayın kamerası yönetmeninin takip ve sabit çekimleri, `cs_win_panel_match`, ... |
| `state` | nesne[] | oyun durumunun değiştiği yerler: zaman, alan, değer - molalar (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, hayatta olan oyuncular, sunucunun `match_start_time` ve `round_start_time` |
| `selfCheck` | nesne | `completeness`: demonun her şeyi nereye gitti - her olay adı, özellik sınıfı, ağ mesajı, kare ve dize tablosu için `seen`, `decoded`, `partial`, `raw` ve `lost` sayıları, yazılan yan dosyalar, toplam `lost` (`--no-bulk` dışında 0), çözümleyicinin listelediği ama okuyamadığı özellikler (`unreadProps`). Kural: [Dönüştürücüler her şeyi tutar](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); yan dosyalar: README'nin Tamlık bölümü |

## Raundlar {#rounds}

| Alan | Tür | Ne |
|---|---|---|
| `number` | sayı | raund, 1'den başlar |
| `start` | sayı | dondurma süresi bittiğinde maç saniyesi |
| `end` | sayı | raundun karara bağlandığı maç saniyesi |
| `until` | sayı | bir sonraki raundun başladığı maç saniyesi (sonrası aşamasının sonu) |
| `winner` | dizge | `T` veya `CT`; berabere için boş |
| `winnerTeam` | dizge | kazanan tarafın takım adı; berabere için boş |
| `reason` | dizge | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` veya `other` |
| `score` | nesne | takım adı -> bu raundan sonra kazanılan raund sayısı |
| `sides` | nesne | takım adı -> bu raundaki `T` / `CT` |
| `equipment` | nesne | taraf -> dondurma süresinin bitişinde yaşayan oyuncularının toplam ekipman değeri, dolar cinsinden |
| `buy` | nesne | taraf -> `pistol`, `eco`, `force` veya `full` |
| `plant` | nesne veya null | bomba kurulumu: `site` (`A` veya `B`; demo söylemiyorsa boş), `time` (raund **içindeki** saniye, bir öldürmenin gibi), `player`, `steamid`, `x`, `y`, `z` (oyun birimleri), `place` (kurucunun yer adı: bombanın durduğu yer) |
| `survivors` | nesne | taraf -> karara bağlandığında hâlâ yaşayan başlangıç oyuncularının adları, sıralı |
| `clutches` | nesne[] | her biri: `player`, `steamid`, `side`, `against` (oyuncu son kalan olduğunda hayatta olan düşmanlar), `won` |
| `kills` | nesne[] | raundun her ölümü, sırayla - aşağıda |

Bunların nasıl bulunduğu: [Maç oluşturma](building-matches.md#rounds);
clutch'lar ve hayatta kalanlar: [İstatistikler](statistics.md#clutches).

### Bir raundun öldürmeleri {#a-rounds-kills}

Raundaki her ölüm, sonrası aşaması dahil:

| Alan | Tür | Ne |
|---|---|---|
| `time` | sayı | raund **içindeki** saniye (dondurma süresinin bitişinden beri) |
| `attacker`, `attackerSide` | dizge | katil ve tarafı; dünya için boş |
| `victim`, `victimSide` | dizge | kurban ve tarafı |
| `assister` | dizge veya null | asist yapan oyuncu, veya null |
| `flashAssist` | bool | asist bir flaştı |
| `weapon` | dizge | oyunun adlandırdığı gibi |
| `headshot` | bool | |
| `wallbang` | bool | mermi bir şeyin içinden geçti |
| `throughSmoke` | bool | öldürme duman içinden yapıldı |
| `noscope` | bool | dürbünlü bir silah dürbünsüz ateşlendi |
| `attackerBlind` | bool | katil flaşlanmıştı |
| `opening` | bool | raundun bir düşmanın ilk öldürmesi |
| `traded` | bool | bu ölüm 5 s içinde intikamı alındı |
| `trade` | bool | bu öldürme 5 s içinde bir takım arkadaşının intikamını aldı |
| `teamkill` | bool | saldırgan ve kurban aynı tarafta, iki farklı oyuncu |
| `suicide` | bool | saldırgan ve kurban aynı oyuncu (kendi bombası gibi); takım arkadaşı öldürmesi değil |
| `after` | bool | öldürme, raund karara bağlandıktan sonra oldu |
| `place` | dizge | **kurbanın** nerede olduğu (haritanın yer adı) |

## Oyuncular {#players}

Oyuncu başına bir giriş, takım adına göre ve sonra en iyisi başta, öldürme eksi ölüm, sonra öldürme:

| Alan | Tür | Ne |
|---|---|---|
| `name`, `steamid`, `team` | dizge | kim |
| `kills`, `deaths` | sayı | |
| `assists`, `flashAssists` | sayı | flaşsız ve flaşlı asistler |
| `diff` | sayı | öldürme - ölüm |
| `adr` | sayı | oynanan raund başına ortalama hasar, kaybedilen can |
| `kast` | sayı | bir öldürme, asist, hayatta kalma veya takas edilmiş bir ölümle oynanan raundların yüzdesi |
| `headshotPct` | sayı | kafa vuruşu olan öldürmelerin yüzdesi |
| `openingKills`, `openingDeaths` | sayı | kazanılan ve kaybedilen açılış düellosu |
| `tradeKills`, `tradedDeaths` | sayı | takas öldürmeleri; takas edilen ölümler |
| `multiKills` | nesne | `{"2k": n, "3k": n, "4k": n, "5k": n}`: o kadar öldürmesi olan raundlar |
| `clutches`, `clutchesWon` | sayı | |
| `utilityDamage` | sayı | HE, molotov ve incendiary ile hasar |
| `enemiesFlashed` | sayı | en az 1 s körleştirilen düşmanlar |
| `plants`, `defuses` | sayı | |
| `teamkills` | sayı | öldürülen takım arkadaşları; intiharlar sayılmaz |
| `roundsPlayed` | sayı | başlayan raundlar |

Her tanım: [İstatistikler](statistics.md#the-scoreboard-line).

## Tanımlar {#conventions}

Sayıların ne anlama geldiğini, bu sayfaya bakmadan bilmek için her belgeye yazılır:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Bir örnek {#an-example}

Testlerdeki sentetik iki raundluk demodan, kısaltılmış (`...` çıkarılanları gösterir):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

`survivors`, `equipment` ve `buy` içindeki anahtarların sırası sabit değildir.
