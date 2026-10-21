# Como contribuir com o atlas de Rio Paranaíba

Toda mudança segue o mesmo caminho:

1. **Issue** descrevendo o que vai ser feito (modelos em *New issue*).
2. **Branch** a partir da `main`, com prefixo do tipo: `dados/…`, `texto/…`, `campo/…`, `config/…`.
3. **Commits pequenos**, um por passo, com mensagem que diga o que mudou (`[DADOS] Catálogo do INEP de nov/2026`).
4. Antes do PR: `python ../atlas-motor/scripts/validar.py` (0 erros).
5. **Pull request** com o modelo preenchido. O workflow *Verificar* precisa ficar **verde**; a coordenação revisa e mescla. Ninguém mescla o próprio PR.

Código não entra aqui: scripts, consultas e esquemas comuns, mapas e o modelo do livro são do [atlas-motor](https://github.com/youthmappers-ufv/atlas-motor). Uma melhoria que sirva a todos os municípios vira issue ou PR lá.

## 1. Edições no OpenStreetMap

- Sempre manuais, com a sua conta, comentário descritivo e as hashtags `#youthmappersufv #ymufv-atlas`, sempre juntas.
- Nada de edição automática ou em lote. Bases oficiais servem só para conferência.
- O que foi conferido em campo vai para `dados/curados/levantamentos-campo.csv` (seção 3).

## 2. Bases oficiais (`dados/oficiais/`)

1. Baixe da fonte oficial, filtre para o município (IBGE 3155504) e salve em CSV UTF-8.
2. Crie a pasta `dados/oficiais/<base>/` com o CSV e o `fonte.toml` (modelo em [dados/oficiais/LEIAME.md](dados/oficiais/LEIAME.md)).
3. PR `[DADOS] …`. O validador confere fonte, licença, data, colunas e coordenadas.

Sem dado pessoal: nomes de profissionais, telefones pessoais, e-mails e CPF não entram.

## 3. Dados levantados pela equipe (`dados/curados/`)

- **Conferência em campo:** `levantamentos-campo.csv`, uma linha por item verificado (id `LC-AAAA-NNN`, data, tema, item, situação, objeto e *changeset* do OSM quando houver).
- **Calendário de eventos:** `eventos-culturais.csv`.
- Os esquemas (colunas, tipos, valores aceitos) estão no catálogo do motor. Um conjunto de dados que só exista aqui ganha esquema em `dados/esquemas/`.

Coordenadas em graus decimais (WGS 84), com ponto: `-19.1965`.

## 4. Pranchas (`atlas/`)

- Para abrir uma prancha: `python ../atlas-motor/scripts/ativar_tema.py <tema>`. O script muda a situação em `temas.toml` e cria `atlas/pranchas/<nn>-<tema>.qmd`; depois, rode `baixar_osm.py --tema <tema>` e escreva o texto.
- O texto da prancha é da equipe; mapas, indicadores e lacunas entram pelo `include`, gerados pelo motor.
- Veja o resultado com `python ../atlas-motor/scripts/construir.py --renderizar html`.

## 5. Atualizar o motor

Quando sair uma versão nova do atlas-motor: `python ../atlas-motor/scripts/atualizar_motor.py --versao vX.Y.Z` (troca no `atlas.toml` e nos workflows), num PR próprio, `[CONFIG] Motor vX.Y.Z`. Leia o `CHANGELOG.md` do motor antes.

## 6. Edições do atlas

A coordenação cria a tag (`git tag v1.0 && git push origin v1.0`) quando uma etapa se fecha. O workflow *Publicar atlas* gera site e PDF daquela versão em `/rio-paranaiba/edicoes/v1.0/` e como versão principal.
