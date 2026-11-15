---
title: "Одржавање ових страница"
nav_order: 17
lang: "sr"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Одржавање ових страница {#maintaining-these-pages}

Контролна листа за свако издање. Странице морају казати шта код ради, бити читљиве почетнику, осмогодишњаку и стручњаку, и постојати на сваком језику који подржава прегледач 3DHeat.

## Контролна листа издања {#release-checklist}

1. **Поново направите генерисане странице** из кода:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Пре commit-а, исто с `--check` мора да изађе са 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Упоредите функције од последњег издања.** `VERSION` држи верзију; њена ознака је `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Свака нова команда, опција, колона, излаз или понашање добија ред на страници која га покрива, и ред у `CHANGELOG.md` под **Docs** с именом те странице.

3. **Независни преглед.** Неко ко није написао промену чита измењене странице - и дијаграме и слике - три пута: као почетник (никад није користио терминал), као осмогодишњак (да ли први пасус каже шта је и зашто, простим речима?) и као стручњак (да ли су заставице, подразумевана подешавања и колоне баш оно што код ради?).

4. **Поправите оно што је преглед нашао.** Слике остају највише око 900 px широке, са текстом од најмање 12 px као што је приказано; дијаграми се праве из `tools/diagrams/*.json` помоћу `tools/flow2svg.py`. Примери користе само измишљена имена (`de_x`, "Demo Valley", `<map>`): никад стварну мапу, играча, ид меча или лик из правих фајлова.

5. **Преводи.** Свака преведена страница бележи хеш енглеског изворника из ког је направљена. Поново превести странице чији се хеш енглеског извора променио, па сваки језик прегледа на исти начин на три начина (једноставно, за почетника, стручно), укључујући ознаке на дијаграмима.

6. **Слање на сервер само уз одобрење власника.** Commit локално; власник одлучује када ће бити јавно.

## Преводи: команде {#translations-the-commands}

Сајт је преведен на 40 језика које подржава прегледач 3DHeat: енглески је у `docs/`, сваки други језик у `docs/<lang>/` с истим именима фајлова. `tools/docs_i18n.py` води евиденцију:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Преводите само оно што `todo` наводи: задржите Markdown, везе, код, називе фајлова и колона онаквим какви јесу, преведите наслове и описе слика, и користите сопствене речи прегледача 3DHeat за његова дугмад и панеле (његов `src/i18n/locales/<lang>/`). Генерисане референтне странице и терминалне слике остају на енглеском. На сајту застарели превод то каже и повезује енглеску страницу; недостајући се враћа на енглески. Језички мени у заглављу и преусмеравање на основу језика прегледача на почетној страници долазе из `docs/_includes/`.
