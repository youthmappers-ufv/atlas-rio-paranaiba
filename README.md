# Atlas Colaborativo de Rio Paranaíba (MG)

Repositório do atlas de **Rio Paranaíba** (IBGE 3155504), do Programa Youthmappers UFV. Guarda só o que é deste município: configuração, dados e textos. O código e a estrutura comuns ficam no [atlas-motor](https://github.com/youthmappers-ufv/atlas-motor), na versão declarada em `atlas.toml` (`motor.versao`).

- **Site e PDF:** https://youthmappers-ufv.github.io/atlas-rio-paranaiba/
- **Hashtags nas edições do OSM:** `#youthmappersufv #ymufv-atlas` (sempre juntas)

> **Tudo aqui é público**, inclusive o histórico, as branches, as issues e os pull requests, a partir do momento em que são enviados. Só entram dados públicos: nada de nomes de moradores ou informantes, telefones, e-mails, CPF ou fotos de fichas. Veja a seção "Dados públicos" do [CONTRIBUTING.md](CONTRIBUTING.md).

## Como citar

SMARZARO, Rodrigo (coord.). **Atlas Colaborativo de Rio Paranaíba**: mapas abertos do município, a partir do OpenStreetMap. Rio Paranaíba: Universidade Federal de Viçosa, Programa Youthmappers UFV, 2026. Disponível em: <https://youthmappers-ufv.github.io/atlas-rio-paranaiba/>. Acesso em: *data do acesso*.

Em BibLaTeX (estilo `abnt` do pacote biblatex-abnt):

```bibtex
% Acrescente urldate = {AAAA-MM-DD}, a data do acesso.
@book{atlas-rio-paranaiba,
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
