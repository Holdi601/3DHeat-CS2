---
title: Manter estas páginas
nav_order: 17
lang: "pt"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Manter estas páginas {#maintaining-these-pages}

A lista de verificação para cada versão. As páginas precisam dizer o que o código faz, ser lidas bem
para um principiante, para uma criança de 8 anos e para um profissional, e existir em todas as
línguas que o visualizador 3DHeat suporta.

## Lista de verificação da versão {#release-checklist}

1. **Regenerar as páginas geradas** a partir do código:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Antes de fazer commit, o mesmo com `--check` precisa sair com 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Comparar as funcionalidades desde a última versão.** `VERSION` tem a versão; o seu rótulo é
   `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Cada novo comando, opção, coluna, saída ou comportamento tem uma linha na página que o cobre, e
   uma linha em `CHANGELOG.md` sob **Docs** a indicar essa página.

3. **Revisão independente.** Alguém que não escreveu a alteração lê as páginas alteradas - incluindo
   diagramas e imagens - três vezes: como principiante (nunca usou um terminal), como criança de 8
   anos (o primeiro parágrafo diz o que é e porquê, em palavras simples?) e como profissional (as
   opções, os valores padrão e as colunas são exatamente o que o código faz?).

4. **Corrigir o que a revisão encontrou.** As imagens ficam com cerca de 900 px de largura no máximo
   e com texto de pelo menos 12 px, tal como são mostradas; os diagramas são gerados a partir de
   `tools/diagrams/*.json` com `tools/flow2svg.py`. Os exemplos usam só nomes inventados (`de_x`,
   "Demo Valley", `<mapa>`): nunca um mapa, jogador, id de partida ou figura real de ficheiros reais.

5. **Traduções.** Cada página traduzida regista o hash do texto inglês de que foi feita. Traduzir de
   novo as páginas cujo hash do texto inglês mudou, e depois fazer rever cada língua das três formas
   (simples, principiante, profissional), incluindo os rótulos dos diagramas.

6. **Enviar só com a aprovação do dono.** Faça commit localmente; o dono decide quando é publicado.

## Traduções: os comandos {#translations-the-commands}

O site está traduzido para as 40 línguas do visualizador 3DHeat: o inglês em `docs/`, cada outra
língua em `docs/<lang>/` com os mesmos nomes de ficheiro. `tools/docs_i18n.py` faz a contabilidade:

```bash
python tools/docs_i18n.py hashes             # depois de qualquer alteração do inglês: regista o hash de cada página
python tools/docs_i18n.py svg-strings        # depois de qualquer alteração de imagem: as etiquetas a traduzir
python tools/docs_i18n.py status             # por língua: atuais, desatualizadas, páginas em falta
python tools/docs_i18n.py todo --lang de     # as páginas alemãs a (re)traduzir
python tools/docs_i18n.py svg-build --lang de    # as imagens alemãs a partir de docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marca as páginas alemãs com o hash do inglês
python tools/docs_i18n.py check              # sai com 1 quando hashes ou etiquetas estão desatualizados
```

Traduza só o que `todo` lista: mantenha o Markdown, as ligações, o código, os nomes de ficheiros e de
colunas tal como estão, traduza os títulos e as descrições das imagens, e use as palavras do próprio
visualizador 3DHeat para os seus botões e painéis (em `src/i18n/locales/<lang>/`). As páginas de
referência geradas e as imagens do terminal ficam em inglês. No site, uma tradução desatualizada
diz isso e liga à página inglesa; uma tradução em falta recorre ao inglês. O menu de línguas do
cabeçalho e o redirecionamento da página inicial pelo idioma do navegador vêm de `docs/_includes/`.
