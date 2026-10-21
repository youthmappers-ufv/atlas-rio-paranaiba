# Atlas Colaborativo de Rio Paranaíba

Repositório **operacional** do projeto de extensão *Atlas Colaborativo do Município* (EXT-ATLAS, RAEX PRJ-211/2026), do Programa Youthmappers UFV. Aqui ficam os dados, as consultas, os scripts e os textos que geram o atlas, como **site** e como **PDF**.

| Repositório | Visibilidade | O que guarda |
|---|---|---|
| `youthmappers-ufv/atlas-rio-paranaiba` (este) | privado: coordenador e estudante | dados, consultas, scripts, textos das pranchas, CI |
| `youthmappers-ufv/atlas` | público | **só o resultado**: site e PDF gerados por `publicar.yml` ([youthmappers-ufv.github.io/atlas](https://youthmappers-ufv.github.io/atlas/)) |
| `youthmappers-ufv/youthmappers-ufv-docs` | privado | parte institucional: proposta, relatórios à UFV, bibliografia, divulgação, orientação do estudante (`projetos/ext-atlas/`) |

A maior parte do mapeamento vai para o próprio **OpenStreetMap**; este repositório guarda o que o atlas precisa além disso.

## Estrutura

```
atlas.toml              município, hashtags, servidores Overpass, parâmetros de completude, publicação
temas.toml              pranchas: id, número, título, situação, consulta, base de referência, recorte
consultas/              uma consulta Overpass por tema ({{bbox}} = caixa do município)
dados/
  osm/                  retrato do OSM: limite.geojson, <tema>.geojson, retrato.json (data da base)
  oficiais/<base>/      bases oficiais (INEP, CNES, Prefeitura) + fonte.toml  → dados/oficiais/LEIAME.md
  curados/              dados levantados pela equipe (CSV)
  esquemas/             esquema de cada CSV de curados/ (colunas, tipos, valores)
scripts/
  baixar_osm.py         baixa o retrato do OSM
  validar.py            integridade do repositório (o CI roda em todo PR)
  indicadores.py        completude C_t e Q_t; indicadores internos
  mapas.py              mapas das pranchas (matplotlib)
  construir.py          prepara tudo para o Quarto (atlas/_gerado/)
atlas/                  livro Quarto: site e PDF (pranchas/<nn>-<tema>.qmd com o texto da equipe)
testes/                 testes dos scripts, com defeitos plantados numa cópia
docs/                   configuração do GitHub e decisões
.github/                workflows (verificar, atualizar-dados, publicar) e modelos de issue e PR
```

## Uso local

Requisitos: Python 3.11+, `pip install -r requirements.txt` (só o matplotlib) e [Quarto](https://quarto.org). Para o PDF, uma distribuição LaTeX (TinyTeX: `quarto install tinytex`, ou MiKTeX).

```bash
python scripts/validar.py                    # 0 erros antes de qualquer PR
python -m unittest discover -s testes        # testes dos scripts
python scripts/baixar_osm.py                 # novo retrato do OSM (ou deixe o CI fazer, todo mês)
python scripts/construir.py                  # indicadores, mapas e trechos das pranchas
quarto render atlas                          # site e PDF em atlas/_site/
quarto preview atlas                         # site no navegador, atualizando ao salvar
```

## Fluxo de trabalho

Tudo entra por **pull request**, com o workflow *Verificar* verde e revisão do coordenador; os procedimentos de cada tipo de contribuição estão em [CONTRIBUTING.md](CONTRIBUTING.md). Edições no OpenStreetMap levam sempre `#youthmappersufv #ymufv-atlas`.

| Workflow | Quando | O que faz |
|---|---|---|
| Verificar | todo PR e push na `main` | testes, `validar.py`, construção do site |
| Atualizar dados do OSM | dia 1 de cada mês, ou manual | baixa o retrato, valida e abre PR com as diferenças |
| Publicar atlas | tag `v*`, dia 5 de cada mês, ou manual | gera site e PDF e publica em `youthmappers-ufv/atlas` (principal ou `/edicoes/<tag>/`) |

**Edições numeradas:** uma tag `vX.Y` na `main` publica a edição com os dados versionados naquele commit (ex.: `v1.0` = atlas web v.1, pranchas 1 a 4). Com o botão manual, dá para publicar qualquer branch, tag ou commit, com os dados versionados ou baixados na hora.

Configuração inicial dos repositórios, do acesso e da chave de publicação: [docs/configuracao-github.md](docs/configuracao-github.md). Licenças: [LICENCAS.md](LICENCAS.md).
