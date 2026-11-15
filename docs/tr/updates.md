---
title: Güncellemeler
nav_order: 14
lang: "tr"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Güncellemeler {#updates}

3DHeat CS2, kendini bu deponun [GitHub sürümlerinden](https://github.com/Holdi601/3DHeat-CS2/releases) güncel tutar. Kod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Başlangıçta kontrol {#the-check-at-start-up}

Her `python -m heat3d_cs2 ...` çalışması önce daha yeni bir sürümün çıkıp çıkmadığını sorar, argümanlarını bile okumadan:

1. Kurulu sürüm, deponun kökündeki `VERSION` dosyasıdır (okunamazsa `0`).
2. En yeni sürüm `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest` adresinden **5 saniye** zaman aşımıyla istenir.
   Cevap **6 saat** boyunca `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` içinde önbelleğe alınır (`LOCALAPPDATA` olmayan
   sistemlerde: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), böylece istek en fazla altı saatte bir yapılır. "Henüz bir sürüm
   yok" (HTTP 404) bir cevap gibi önbelleğe alınır. Çevrimdışı, istek sınırına takılmış, bir vekil sunucunun arkasında - diğer her hata -
   araç sahip olduğu sürümle devam eder ve hiçbir şey önbelleğe alınmaz.
3. Sürümler sayı olarak karşılaştırılır: `v1.2.3` ve `1.2.3` eşittir, bir `-` veya `+`'dan sonrası yok sayılır, eksik parçalar 0 sayılır.

Daha yeni bir sürüm çıktığında, bunu hata akışında söyler:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Bir terminalde (hem girdi hem hata akışı terminaldir) sorar. Enter, `y`, `yes`, `j` veya `ja` güncellenir; başka her şey
  değişmeden devam eder. Güncellemeden sonra **aynı komut yeniden çalışır**, yeni kodla.
- Bir terminal olmadan - zamanlanmış bir çalışma, bir boru - yalnızca güncellemenin nerede yapılacağını yazar ve devam eder:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` kontrolü kapatır. Boş, `0`, `false` veya `no` dışındaki her değer açık sayılır.

## İstek üzerine güncelleme {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Bu her zaman GitHub'a sorar (önbellek kullanılmaz). `Up to date: <version>.`, `No release found (this is <version>); offline, or nothing published yet.`
veya `<new> is out (this is <current>): <url>` yazar ve sonra günceller (`--check` değilse). Bir güncelleme denenip başarısız olursa çıkış kodu
`1`, aksi halde `0`.

## Güncelleme nasıl uygulanır {#how-an-update-is-applied}

Kopyanın nasıl kurulduğuna bağlıdır:

- **Bir git kopyası** (kökte bir `.git` ve `PATH` üzerinde `git`): `git pull --ff-only`. İzlenen dosyalarda yerel değişiklikler varken
  reddedilir ("this checkout has local changes; commit or stash them, then run `git pull`"): bunlar birinin işidir ve bir güncelleme
  bunların ne olacağına karar vermez. İzlenmeyen dosyalar engellemez.
- **İndirilmiş bir kopya**: sürümün kaynak arşivi (GitHub'ın zipball'u) indirilir ve geçici bir klasöre açılır - dışarıya çıkacak girdiler
  atlanır - ve onun `VERSION`'ı sürümün iddia ettiği sürüm olmalıdır, yoksa hiçbir şey değişmez ("the archive is version X, not Y").
  Sonra dosyaları klasörün üzerine kopyalanır. Sürümün parçası olmayan dosyalar - demolarınız, çıktılarınız, sanal ortamınız, yaptığınız her şey -
  asla dokunulmaz. Sürümün artık olmadığı Python modülleri, aracın kendi paketlerinden (`heat3d_*` klasörleri) silinir, böylece eski bir modül
  yerine geçeni gölgelemez.

Bir güncelleme başarısız olursa mesaj yazdırılır ve araç sahip olduğu sürümle çalışmaya devam eder.
