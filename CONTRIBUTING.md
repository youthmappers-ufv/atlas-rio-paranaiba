# Como contribuir com o atlas

Toda mudança neste repositório segue o mesmo caminho:

1. **Issue** descrevendo o que vai ser feito (modelos em *New issue*).
2. **Branch** a partir da `main`, com prefixo do tipo: `dados/…`, `texto/…`, `campo/…`, `codigo/…`.
3. **Commits pequenos**, um por passo, com mensagem que diga o que mudou (`[DADOS] Catálogo do INEP de nov/2026`).
4. Antes do PR, no seu computador: `python scripts/validar.py` (0 erros) e `python -m unittest discover -s testes`.
5. **Pull request** com o modelo preenchido. O workflow *Verificar* precisa ficar **verde**; o coordenador revisa e mescla. Ninguém mescla o próprio PR.

## 1. Edições no OpenStreetMap

O mapeamento em si acontece no OSM, não aqui.

- Sempre manual, com a sua conta, comentário descritivo e as hashtags `#youthmappersufv #ymufv-atlas`, sempre juntas.
- Nada de edição automática ou em lote. Bases oficiais servem só para conferência.
- Na dúvida sobre etiquetas, consulte a wiki do OSM e anote a decisão em `docs/decisoes.md`.
- O que você conferiu em campo vai para `dados/curados/levantamentos-campo.csv` (seção 3). Assim a conferência fica registrada mesmo quando nada muda no mapa.

## 2. Bases oficiais (`dados/oficiais/`)

Para carregar ou atualizar o Catálogo de Escolas do INEP, o CNES, listas da Prefeitura etc.:

1. Baixe da fonte oficial; filtre para o município (IBGE 3155504); salve em CSV UTF-8.
2. Crie ou atualize a pasta `dados/oficiais/<base>/` com o CSV e o `fonte.toml` (modelo em [dados/oficiais/LEIAME.md](dados/oficiais/LEIAME.md)).
3. Se for base nova, ligue o tema a ela em `temas.toml` (`referencia = "<base>"`).
4. PR `[DADOS] …`. O validador confere fonte, licença, data, colunas e coordenadas.

Sem dado pessoal: nomes de profissionais, telefones pessoais, e-mails e CPF não entram. O CI recusa e-mails e CPFs.

## 3. Dados levantados pela equipe (`dados/curados/`)

Cada CSV tem um esquema em `dados/esquemas/` que diz as colunas, os tipos e os valores aceitos.

- **Conferência em campo:** `levantamentos-campo.csv`, uma linha por item verificado (id `LC-AAAA-NNN`, data, tema, item, situação, objeto e *changeset* do OSM quando houver).
- **Calendário de eventos** (prancha de cultura e turismo): `eventos-culturais.csv`.
- **Novo conjunto de dados:** crie primeiro o esquema em `dados/esquemas/<nome>.toml` (copie um existente) e o CSV com o cabeçalho, no mesmo PR.

Edite os CSV em editor de texto ou planilha que salve em UTF-8 com vírgula. Coordenadas em graus decimais (WGS 84), com ponto: `-19.1965`.

## 4. Textos das pranchas (`atlas/`)

- Cada prancha é `atlas/pranchas/<nn>-<tema>.qmd`: o texto é da equipe; mapas, indicadores e lacunas entram sozinhos pelo `{{< include ../_gerado/<tema>.md >}}`.
- Para **abrir uma prancha nova**: em `temas.toml`, mude a situação de `planejado` para `em-andamento`; crie o `.qmd` (copie um existente); acrescente-o aos capítulos de `atlas/_quarto.yml`. O validador confere os três.
- Veja o resultado com `python scripts/construir.py` e `quarto preview atlas`.

## 5. Consultas, scripts e configuração

- Consultas Overpass em `consultas/`, sempre com `{{bbox}}`; mudar uma consulta muda o retrato, então rode `python scripts/baixar_osm.py --tema <id>` no mesmo PR.
- Scripts com a biblioteca padrão do Python, exceto os mapas (matplotlib). Toda regra nova do validador ganha um teste em `testes/` com o defeito plantado numa cópia.
- Mudanças em `atlas.toml` e nos workflows passam pelo coordenador.

## 6. Retrato do OSM (`dados/osm/`)

Não edite à mão: é gerado por `scripts/baixar_osm.py`. Todo dia 1, o workflow *Atualizar dados do OSM* abre um PR com o retrato novo. Revise as mudanças (o diff mostra cada feição) e mescle.

## 7. Edições do atlas

O coordenador cria a tag (`git tag v1.0 && git push origin v1.0`) quando uma etapa do cronograma se fecha. O workflow *Publicar atlas* gera site e PDF daquela versão e publica em `/edicoes/v1.0/` e como versão principal.
