---
title: Demo okuma
nav_order: 5
lang: "tr"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Demo okuma {#reading-a-demo}

Bir `.dem` dosyasından, herhangi bir yorumlamadan önce neyin çıkarıldığı. Kod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Bir CS2 demosu, sunucunun kendi kaydıdır (SourceTV): her oyuncu, her tik, saniyede 64 tik (`TICKRATE = 64`). Üç çağrıyla
[demoparser2](https://github.com/LaihoE/demoparser) ile okunur ve sonuç geldiği gibi bir `RawPart` içinde tutulur:

| Alan | Neyi tutar |
|---|---|
| `path` | dosya |
| `map` | demo başlığındaki `map_name` (`de_x`); başlık bir tane vermiyorsa boş |
| `samples` | tik başına oyuncu başına bir satır: aşağıdaki oyuncu ve kural alanları, artı `tick`, `steamid`, `name` |
| `events` | olay adı -> satırları, oyuncu alanları çözümleyicinin adlandırdığı gibi `user_`, `attacker_`, `assister_` önekiyle |

`demo.py` içinde hiçbir şey bir raundun ne olduğuna veya kimin kazandığına karar vermez; bu, [Maç oluşturma](building-matches.md)
sayfasının işidir.

## Örneklenen tikler {#the-sampled-ticks}

`parse_ticks`, `0, N, 2N, ...` tiklerini `4,000,000`'a kadar ister (`LAST_TICK`, herhangi bir maçtan çok uzak - saniyede
64 tikle 17 saat), burada *N*, `--every` değeridir (varsayılan 8). Ayrıştırıcı demonun sonunda durur. Örneklenmiş her tikte
mevcut her oyuncu bir satır verir - hayatta, ölü, izleyen veya antrenör olsun; filtreleme daha sonra yapılır.

Örnekleme adımı, ısı haritasının yoğunluğunun ötesinde önemlidir: bir raundun ne zaman karara bağlandığı bu örneklerden okunur
(bkz. [Maç oluşturma](building-matches.md#rounds)), bu yüzden raund bitiş zamanları bir adım doğruluğundadır (varsayılan olarak
1/8 s).

### Oyuncu alanları {#player-fields}

| Özellik | Olur |
|---|---|
| `X`, `Y`, `Z` | konum, oyunun birimlerinde (inç), Z yukarı. demoparser2 oyuncunun orijinini, yani ayaklarını verir. |
| `yaw`, `pitch` | bakış yönü (derece), bir birim vektöre çevrilmiş |
| `health`, `armor_value` | can, zırh |
| `team_num` | taraf: 2 = T, 3 = CT; başka her şey (izleyiciler, 0, 1) taraf değildir |
| `team_clan_name` | sunucunun gösterdiği takım adı, takımları adlandırmak için kullanılır |
| `active_weapon_name` | elde tutulan silah, oyunun adlandırdığı gibi (`AK-47`, `Karambit`) |
| `is_alive` | oyuncunun hayatta olup olmadığı - yalnızca yaşayan oyuncular konum olur |
| `last_place_name` | haritanın kendi yer adı (`BombsiteA`) |
| `balance` | para |
| `current_equip_value` | oyuncunun taşıdıklarının değeri |

### Oyun kuralı alanları {#game-rules-fields}

Yanında okunur, oyuncu satırı başına bir kez (tik başına herkes için aynıdırlar):

| Özellik | Kullanım |
|---|---|
| `game_time` | sunucunun saati, saniye cinsinden |
| `total_rounds_played` | raund sayısı, bir maçın dosyaları boyunca devam eder |
| `round_win_status` | az önce oynanan raundu kim kazandı: 1 berabere, 2 T, 3 CT |
| `round_win_reason` | nasıl (oyunun `CSRoundEndReason`'ı) |
| `team_rounds_total` | her tarafın skoru |
| `is_warmup_period` | ısınma her yerde dışarıda bırakılır |
| `is_freeze_period` | dondurma süresi konumlardan dışarıda bırakılır |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | oynanan uzatma, normal sürede 0: uzatma raundları tabanca raundu değildir (ayrıştırıcının daha kısa bir adı yoktur) |

## Olaylar {#the-events}

Aşağıdaki her olay, demo onu bildirdiğinde okunur (`list_game_events`); olayın adlandırdığı her oyuncu için `X`, `Y`, `Z`,
`team_num`, `last_place_name` ve `which_bomb_zone` (oyuncunun durduğu bomba bölgesi: 0 yok, 1 A, 2 B) ve o tikteki oyunun
`total_rounds_played` ve `is_warmup_period` değerleri ile:

| Olay | Olur |
|---|---|
| `player_death` | öldürmeler ve ölümler; `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` kullanılır |
| `player_hurt` | hasar; `dmg_health` (sağlığa verilen hasar), `health` (kalan can), `weapon` kullanılır |
| `player_blind` | flaşlanan oyuncular; `blind_duration` kullanılır |
| `weapon_fire` | atışlar ve bomba fırlatmaları; `weapon` kullanılır |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | bombaların nerede patladığı; olayın kendi `x`, `y`, `z` değerleri kullanılır (olayın o nokta için bir yer adı yoktur, yalnızca fırlatanın) |
| `bomb_planted` | kurulum; kurucunun `which_bomb_zone` ve yeri kullanılır, ayrıca `site` (bölgenin varlık numarası) |
| `bomb_defused` | etkisizleştirme |
| `bomb_exploded` | bombanın ne zaman patladığı: `explode` satırının zamanı |
| `round_freeze_end` | her raundun nerede başladığı |
| `round_prestart` | karara bağlanmış bir raundan sonraki sürenin nerede bittiği |
| `round_announce_match_start` | canlı maçın nerede başladığı |

## Demolar hakkında, nasıl okunduklarını belirleyen iki gerçek {#two-facts-about-demos-that-decide-how-they-are-read}

- **Bir maç dosyalara bölünebilir** ve dosyaların adları sıralarını söylemez. Raund sayısı (`total_rounds_played`) onlar boyunca
  devam eder ve genellikle sunucunun saati de öyle, bu yüzden parçalar içerdiklerinden sıralanabilir.
- **Bir kayıt maçtan önce başlayabilir**: ısınma, yeniden başlatma, bir bıçak raundu. Maç, bir dosyadaki **son**
  `round_announce_match_start` ile başlar; ondan önce her şey dışarıda bırakılır ve ısınma her yerde dışarıda bırakılır.
