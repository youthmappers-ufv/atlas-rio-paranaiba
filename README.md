# Atlas Colaborativo de Rio Paranaíba (MG)

[![site do atlas](https://img.shields.io/badge/atlas-site-blue)](https://youthmappers-ufv.github.io/atlas-rio-paranaiba/) [![Publicar atlas](https://github.com/youthmappers-ufv/atlas-rio-paranaiba/actions/workflows/publicar.yml/badge.svg)](https://github.com/youthmappers-ufv/atlas-rio-paranaiba/actions/workflows/publicar.yml) [![Verificar](https://github.com/youthmappers-ufv/atlas-rio-paranaiba/actions/workflows/verificar.yml/badge.svg?branch=main)](https://github.com/youthmappers-ufv/atlas-rio-paranaiba/actions/workflows/verificar.yml) [![dados do OSM](https://img.shields.io/endpoint?url=https%3A%2F%2Fyouthmappers-ufv.github.io%2Fatlas-rio-paranaiba%2F_gerado%2Fbadges%2Fdados.json)](https://youthmappers-ufv.github.io/atlas-rio-paranaiba/dados.html) [![completude](https://img.shields.io/endpoint?url=https%3A%2F%2Fyouthmappers-ufv.github.io%2Fatlas-rio-paranaiba%2F_gerado%2Fbadges%2Fcompletude.json)](https://youthmappers-ufv.github.io/atlas-rio-paranaiba/) [![motor](https://img.shields.io/endpoint?url=https%3A%2F%2Fyouthmappers-ufv.github.io%2Fatlas-rio-paranaiba%2F_gerado%2Fbadges%2Fmotor.json)](https://github.com/youthmappers-ufv/atlas-motor) [![edição](https://img.shields.io/github/v/release/youthmappers-ufv/atlas-rio-paranaiba?label=edi%C3%A7%C3%A3o)](https://github.com/youthmappers-ufv/atlas-rio-paranaiba/releases) [![dados: ODbL 1.0](https://img.shields.io/badge/dados-ODbL%201.0-brightgreen)](LICENCAS.md) [![textos: CC BY 4.0](https://img.shields.io/badge/textos-CC%20BY%204.0-lightgrey)](LICENCAS.md)

Repositório do atlas de **Rio Paranaíba** (IBGE 3155504), do Programa Youthmappers UFV. Guarda só o que é deste município: configuração, dados e textos. O código e a estrutura comuns ficam no [atlas-motor](https://github.com/youthmappers-ufv/atlas-motor), na versão declarada em `atlas.toml` (`motor.versao`).

- **Site e PDF:** https://youthmappers-ufv.github.io/atlas-rio-paranaiba/
- **Hashtags nas edições do OSM:** `#youthmappersufv #ymufv-atlas` (sempre juntas)

> **Tudo aqui é público**, inclusive o histórico, as branches, as issues e os pull requests, a partir do momento em que são enviados. Só entram dados públicos: nada de nomes de moradores ou informantes, telefones, e-mails, CPF ou fotos de fichas. Veja a seção "Dados públicos" do [CONTRIBUTING.md](CONTRIBUTING.md).

## Como citar

SMARZARO, Rodrigo (coord.). **Atlas Colaborativo de Rio Paranaíba**: mapas abertos do município, a partir do OpenStreetMap. Rio Paranaíba: Universidade Federal de Viçosa, Programa Youthmappers UFV, 2026. Disponível em: <https://youthmappers-ufv.github.io/atlas-rio-paranaiba/>. Acesso em: *data do acesso*.

Em BibLaTeX (estilo `abnt` do pacote biblatex-abnt):

```bibtex
% Acrescente urldate = {AAAA-MM-DD}, a data do acesso.
@dataset{atlas-rio-paranaiba,
  editor     = {Smarzaro, Rodrigo},
  editortype = {coordinator},
  title      = {Atlas Colaborativo de Rio Paranaíba},
  subtitle   = {mapas abertos do município, a partir do {OpenStreetMap}},
  location   = {Rio Paranaíba},
  publisher  = {Universidade Federal de Viçosa, Programa Youthmappers UFV},
  year       = {2026},
  url        = {https://youthmappers-ufv.github.io/atlas-rio-paranaiba/},
  langid     = {brazilian},
}
```

O GitHub também oferece a citação pelo botão *Cite this repository* (arquivo `CITATION.cff`). A página inicial do atlas traz a referência com o ano da edição e o arquivo `.bib` para baixar. Os dados do OpenStreetMap pedem, além disso, a atribuição *© colaboradores do OpenStreetMap (ODbL)*.

## Estrutura

```
atlas.toml        município, versão do motor, hashtags, publicação
temas.toml        situação de cada prancha do catálogo do motor (e pranchas próprias)
consultas/        consultas Overpass próprias (opcional; substituem as do catálogo)
dados/
  osm/            retrato do OSM (gerado; não editar à mão)
  oficiais/       bases oficiais abertas (INEP, CNES, Prefeitura), cada uma com fonte.toml
  curados/        dados levantados pela equipe (CSV, esquemas no catálogo do motor)
  esquemas/       esquemas próprios deste município (opcional)
atlas/            textos: index.qmd (apresentação) e pranchas/<nn>-<tema>.qmd
identidade/       identidade visual própria (opcional): _brand.yml e logos; sem ela, a do programa
.github/          workflows que chamam o motor; modelos de issue e PR
```

## Uso local

Clone o `atlas-motor` **ao lado** deste repositório (`git clone https://github.com/youthmappers-ufv/atlas-motor ../atlas-motor`). Os scripts rodam sozinhos na versão do motor declarada no `atlas.toml`, extraída do clone (mantenha-o com `git -C ../atlas-motor pull --tags`). Requisitos: Python 3.11+, `pip install -r ../atlas-motor/requirements.txt` e [Quarto](https://quarto.org).

```bash
python ../atlas-motor/scripts/instalar_ganchos.py              # uma vez por clone: valida antes de cada push
python ../atlas-motor/scripts/validar.py                        # 0 erros antes de qualquer PR
python ../atlas-motor/scripts/baixar_osm.py                     # retrato novo do OSM
python ../atlas-motor/scripts/ativar_tema.py educacao           # abre uma prancha
python ../atlas-motor/scripts/construir.py --previa             # prévia ao vivo: edite atlas/ e o navegador recarrega
python ../atlas-motor/scripts/construir.py --renderizar todos   # site e PDF em _construcao/livro/_site/
```

Procedimentos de contribuição: [CONTRIBUTING.md](CONTRIBUTING.md). Licenças: [LICENCAS.md](LICENCAS.md). Documentação completa (guia do município, pranchas, identidade visual, referência, solução de problemas): [docs do atlas-motor](https://github.com/youthmappers-ufv/atlas-motor/blob/main/docs/README.md).
