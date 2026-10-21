# Bases oficiais

Cada base fica numa pasta própria (o nome é o que vai em `referencia` no `temas.toml`), com o arquivo de dados em CSV (UTF-8, separado por vírgula) e um `fonte.toml`:

```toml
nome = "Catálogo de Escolas"
orgao = "INEP"
url = "https://www.gov.br/inep/..."        # página de onde foi baixado
data_acesso = 2026-11-10                   # AAAA-MM-DD
licenca = "..."                            # como consta na fonte
arquivo = "escolas-rio-paranaiba.csv"
observacao = "Filtrado para o município 3155504; colunas renomeadas."

[colunas]                                  # quais colunas do CSV fazem cada papel
id = "codigo_inep"
nome = "escola"
lat = "latitude"
lon = "longitude"
```

Regras:

- As bases servem **só para conferência**: nada é copiado delas para o OpenStreetMap.
- Filtre para o município e mantenha só as colunas necessárias. Nada de dado pessoal (no CNES, consultórios de pessoa física não entram com nome do profissional).
- Atualizar uma base = substituir o CSV e a `data_acesso` no mesmo PR; o histórico fica no Git.
- `python scripts/validar.py` confere o `fonte.toml`, as colunas e as coordenadas.
