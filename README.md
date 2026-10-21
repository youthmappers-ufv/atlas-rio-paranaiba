# Atlas Colaborativo de Rio Paranaíba (MG)

Repositório do atlas de **Rio Paranaíba** (IBGE 3155504), do Programa Youthmappers UFV. Guarda só o que é deste município: configuração, dados e textos. O código e a estrutura comuns ficam no [atlas-motor](https://github.com/youthmappers-ufv/atlas-motor), na versão declarada em `atlas.toml` (`motor.versao`).

- **Site e PDF publicados:** https://youthmappers-ufv.github.io/atlas/rio-paranaiba/
- **Hashtags nas edições do OSM:** `#youthmappersufv #ymufv-atlas` (sempre juntas)
- **Projeto:** extensão *Atlas Colaborativo do Município* (EXT-ATLAS, RAEX PRJ-211/2026). A parte institucional (proposta, relatórios à UFV, bibliografia, orientação do estudante) fica em `youthmappers-ufv/youthmappers-ufv-docs`, pasta `projetos/ext-atlas/`.

## Estrutura

```
atlas.toml        município, versão do motor, hashtags, publicação
temas.toml        situação de cada prancha do catálogo do motor (e pranchas próprias)
consultas/        consultas Overpass próprias (opcional; substituem as do catálogo)
dados/
  osm/            retrato do OSM (gerado; não editar à mão)
  oficiais/       bases oficiais (INEP, CNES, Prefeitura), cada uma com fonte.toml
  curados/        dados levantados pela equipe (CSV, esquemas no catálogo do motor)
  esquemas/       esquemas próprios deste município (opcional)
atlas/            textos: index.qmd (apresentação) e pranchas/<nn>-<tema>.qmd
docs/decisoes.md  decisões do município (etiquetas, fontes, temas)
.github/          workflows que chamam o motor; modelos de issue e PR
```

## Uso local

Clone o `atlas-motor` **ao lado** deste repositório, na mesma versão do `atlas.toml` (`git -C ../atlas-motor checkout v1.0`). Requisitos: Python 3.11+, `pip install -r ../atlas-motor/requirements.txt` e [Quarto](https://quarto.org).

```bash
python ../atlas-motor/scripts/validar.py                        # 0 erros antes de qualquer PR
python ../atlas-motor/scripts/baixar_osm.py                     # retrato novo do OSM
python ../atlas-motor/scripts/ativar_tema.py educacao           # abre uma prancha
python ../atlas-motor/scripts/construir.py --renderizar html    # site em _construcao/livro/_site/
python ../atlas-motor/scripts/construir.py --renderizar todos   # site e PDF
```

Procedimentos de contribuição: [CONTRIBUTING.md](CONTRIBUTING.md). Configuração no GitHub: `docs/configuracao-github.md` do atlas-motor.
