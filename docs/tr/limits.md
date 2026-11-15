---
title: Sınırlar
nav_order: 13
lang: "tr"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Sınırlar {#limits}

Dönüştürücünün ne varsaydığı, neyi ele almadığı ve neyin doğrulanmadığı. Her madde mevcut koddan alınmıştır.

## Neyi okur {#what-it-reads}

- **Yalnızca sıkıştırılmamış `.dem` dosyaları.** `.dem.zst`, `.dem.bz2`, `.rar` ve `.zip` önce açılmalıdır.
  Uzantı her harf durumuyla eşleşir (`.dem`, `.DEM`); klasörlerde de, adıyla verilen dosyalarda da aynıdır.
- **Bomba etkisizleştirme maçları.** Raundun bitiş nedenleri, bomba kurulumu ve sitesi, alım türleri ve tabanca
  raundları bomba etkisizleştirme moduna aittir. Rehine haritaları, Wingman ve diğer modlar özel olarak ele
  alınmaz ve doğrulanmamıştır.
- **Saniyede 64 tik** her tikten hesaplanan zaman için varsayılır (`TICKRATE = 64`); CS2 sunucuları 64'te çalışır.
- **Sunucudan bir demo** (SourceTV) varsayılır: her oyuncuyu içerir. İstemci tarafı bir kayıt (POV demo) denenmedi.

## Maçlar ve raundlar {#matches-and-rounds}

- **Dosyalar ada göre gruplanır.** Bir maçın parçaları, bir `-pN` / `_pN` eki dışında aynı ada sahip olmalıdır;
  farklı adlardaki bir maçın dosyaları ayrı maçlar olur ve aynı adlı, farklı klasörlerdeki dosyalar birlikte
  gruplanır (sonra birbirinin devamı değillerse zincirlere ayrılır).
- **Canlı maç, bir dosyadaki son `round_announce_match_start` ile başlar.** Bu açıklamayla izlenmeyen bir bıçak
  raundu bir raund olarak sayılır.
- **Raund bitiş zamanları bir örneğin doğruluğundadır** (`--every` tik, varsayılan olarak 1/8 s), çünkü karar
  örneklenmiş oyun durumundan okunur. Çok büyük bir `--every`, bir raundun bitişi ile bir sonrakinin başlangıcı
  arasındaki kısa bir pencereyi kaçırabilir ve raundu eksik olarak bırakabilir.
- **Berabere.** Berabere biten bir raund (win status 1, reason 10) kazanansız karara bağlanır: `winner` boştur ve
  hiçbir taraf kazanmamıştır. Gerçek bir demoda beraberlik görülmedi, bu sentetik demoda kontrol edilir.
- **Dosyaların sonuyla kesilen raundlar** dışarıda bırakılır (`incomplete`), tahmin edilmez; dosyalardaki ilk
  raundan önceki raundlar `missing` olarak listelenir.
- **Tabanca raundları**, kaydın gösterdiği yarı uzunluğunu izler: ardışık iki normal raund arasında taraflar ilk
  kez yer değiştirdiği yerde. Bu yer değiştirmeyi göstermeyen bir kayıt (yarı molasından sonra başlar, öncesinde
  biter, veya yer değiştirmenin iki yanındaki bir raund eksiktir) yalnızca 1. raundu tabanca raundu olarak bilir.
  Uzatmanın tabanca raundu yoktur.
- **Takımlar.** Bir takım, oyuncularında en çok görülen klan adıdır. Klan adı olmadan takımlar `Started T` ve
  `Started CT`'dir. Maç ortasında takım değiştiren bir oyuncu tek bir takımda kalır.

## Olaylar {#events}

- **Ayrıştırıcının sunduğu her şey okunur**, şu istisnalarla: oyuncuların hızı (ayrıştırıcı bunu konumlardan
  türetir; demoda yoktur), ses (`parse_voice`) ve bombanın `weapon_fire` olayı (bir kurulumun başlangıcı, bunu
  `bomb_beginplant` zaten verir). Bomba uçuşları, oyuncuların örneklenmesinde (`--every`) ve bombanın durduğu
  yerde tutulur, her tikte değil.
- **Bir raundun dışındaki satırlar** (ısınma, maçın başlangıcı ile ilk dondurma süresi arasındaki iki dakikadan
  uzun bir duraklatma) tablodan dışarıda bırakılır; hiçbir oyuncuyla ilgili olmayan olayların hepsi maç
  belgesinin `events` listesindedir.
- **Patlama satırlarında** (`smoke`, `flash`, `he`, `molotov`, `decoy`) `place` yoktur: demo oyuncular için yer
  adı verir, bombalar için vermez. Fırlatanın o andaki yeri `throwerPlace`'tedir.
- **Kurulumun sitesi**, kurucunun durduğunu oyunun söylediği bomba bölgesinden, yoksa kurucunun yer adından, yoksa
  aynı dosyada aynı bölgedeki başka bir kurulumdan gelir. Bunların hiçbiri söylemiyorsa `site` boştur.
- **Dünyaya ölüm** (bir düşme, bomba) saldırgansızdır: öldürme yok, takım arkadaşı öldürmesi yok, açılış yok;
  yalnızca bir ölümdür.

## İstatistikler {#statistics}

- **Oynanan raundlar**, raundun dondurma süresinden sonraki ilk saniyede bir konumu olan oyunculardan gelir. Bir
  raunda geç bağlanan bir oyuncu o raundu oynamış sayılmaz (öldürmeleri yine sayılır).
- **KAST için hayatta kalma**: sonrası aşamasında öldürülen bir oyuncu KAST için hayatta kalmamış sayılır, oysa
  raund listesi onları yine hayatta kalanlar arasında gösterir.
- **Bir 1v1'in iki oyuncusu** aynı raundda clutch kazanmış sayılabilir; bkz.
  [İstatistikler](statistics.md#clutches).
- **Yardımcı hasar**, HE bombaları, molotoflar ve incendiary'lerdir; atılan bir flaşın veya decoy'un öldürmesi
  veya vuruşu yardımcı hasar değildir.

## Harita dışa aktarımı {#map-export}

- Oyunun kurulu olmasını (veya `.vpk`'yı) ve Source2Viewer'ın CLI'sini gerektirir; hiçbir şey indirilmez.
- Yalnızca `world_physics` dışa aktarılır; klip fırçaları ve gökyüzü, adlarında `clip` veya `sky` geçmesiyle
  (harf durumundan bağımsız) dışarıda bırakılır.
- Zemin, yapıdan yalnızca yüz normaliyle ayrılır (Z bileşeni 0.7 veya daha fazla); bu yüzden dik bir rampa yapıdır
  ve düz bir çatı zemindir.
- Dosya metre değil, inç cinsindendir.

## Bellek ve zaman {#memory-and-time}

- Bir maç, oluşturulurken bütünüyle bellekte tutulur, maç başına bir işçide. Çok sayıda işçi ve küçük bir `--every`
  ile bellek toplanır: bir makine yetersiz kalırsa `--jobs` değerini düşürün.
- Bir maç yalnızca oluşturulduğunda yazılır: önce `.parquet`, sonra `.match.json`. Aradaki bir anda durdurulan bir
  çalıştırma, maç belgesi olmayan bir tablo bırakır; bir maç yalnızca ikisiyle birlikte yazılmış sayılır, bu yüzden
  bir sonraki çalıştırma onu yeniden çevirir. Henüz başlamamış maçlar bir sonraki çalıştırmada alınır.
