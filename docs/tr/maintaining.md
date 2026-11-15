---
title: Bu sayfaların bakımı
nav_order: 17
lang: "tr"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Bu sayfaların bakımı {#maintaining-these-pages}

Her sürüm için kontrol listesi. Sayfalar, kodun ne yaptığını söylemeli; bir başlangıç seviyesindeki kişi, 8 yaşındaki
bir çocuk ve bir uzman için iyi okunmalı ve 3DHeat görüntüleyicisinin desteklediği her dilde bulunmalıdır.

## Sürüm kontrol listesi {#release-checklist}

1. **Oluşturulan sayfaları koddan yeniden üretin**:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Commit etmeden önce, `--check` ile aynı komut 0 ile çıkmalıdır:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Son sürümden bu yana olan özellikleri karşılaştırın.** `VERSION` sürümü tutar; etiketi `v<VERSION>`'dır:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Her yeni komut, seçenek, sütun, çıktı veya davranış, onu kapsayan sayfada bir satır alır ve
   `CHANGELOG.md` dosyasında **Docs** altında o sayfayı adlandıran bir satır alır.

3. **Bağımsız inceleme.** Değişikliği yazmamış biri, değişen sayfaları üç kez okur - resimler ve şemalar dahil:
   bir başlangıç seviyesi olarak (hiç terminal kullanmamış), 8 yaşında bir çocuk olarak (ilk paragraf ne olduğunu ve
   neden olduğunu sade sözlerle söylüyor mu?) ve bir uzman olarak (bayraklar, varsayılanlar ve sütunlar kodun tam
   yaptığı şeyler mi?).

4. **İncelemenin bulduklarını düzeltin.** Resimler yaklaşık 900 px genişliğinde kalır, metin gösterildiği gibi en az
   12 px'tir; şemalar `tools/diagrams/*.json` dosyalarından `tools/flow2svg.py` ile üretilir. Örnekler yalnızca uydurma
   adlar kullanır (`de_x`, "Demo Valley", `<map>`): gerçek bir harita, oyuncu, maç kimliği veya gerçek dosyalardan bir
   şekil asla kullanılmaz.

5. **Çeviriler.** Her çevrilmiş sayfa, yapıldığı İngilizce kaynağın karmasını kaydeder. İngilizce kaynağın karması
   değişen sayfaları yeniden çevirin; ardından her dil aynı üç şekilde (sade, başlangıç, uzman) incelensin, şema
   etiketleri dahil.

6. **Yalnızca sahibinin onayından sonra gönderin.** Yerelde commit edin; ne zaman herkese açık olacağına sahip karar verir.

## Çeviriler: komutlar {#translations-the-commands}

Site, 3DHeat görüntüleyicisinin 40 diline çevrilir: İngilizce `docs/` içinde, diğer her dil `docs/<lang>/` içinde
aynı dosya adlarıyla. `tools/docs_i18n.py` kayıtları tutar:

```bash
python tools/docs_i18n.py hashes             # any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Yalnızca `todo`'nun listelediğini çevirin: Markdown, bağlantıları, kodu, dosya ve sütun adlarını olduğu gibi
bırakın, başlıkları ve resim açıklamalarını çevirin ve düğmeler ve paneller için 3DHeat görüntüleyicisinin kendi
sözcüklerini kullanın (`src/i18n/locales/<lang>/` içindekiler). Oluşturulan başvuru sayfaları ve terminal resimleri
İngilizce kalır. Sitede, güncel olmayan bir çeviri bunu söyler ve İngilizce sayfaya bağlanır; eksik olan İngilizceye
düşer. Başlıktaki dil menüsü ve ana sayfanın tarayıcı diline göre yönlendirmesi `docs/_includes/` içinden gelir.
