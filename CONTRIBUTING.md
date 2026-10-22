# Como contribuir com o atlas de Rio Paranaíba

Toda mudança segue o mesmo caminho:

1. **Issue** descrevendo o que vai ser feito (modelos em *New issue*).
2. **Branch** a partir da `main`, com prefixo do tipo: `dados/…`, `texto/…`, `campo/…`, `config/…`.
3. **Commits pequenos**, um por passo, com mensagem que diga o que mudou (`[DADOS] Catálogo do INEP de nov/2026`).
4. Antes do push: `python ../atlas-motor/scripts/validar.py` (0 erros). Com o gancho instalado (`python ../atlas-motor/scripts/instalar_ganchos.py`, uma vez por clone), isso roda sozinho e o push é bloqueado se houver erro.
5. **Pull request** com o modelo preenchido. O workflow *Verificar* precisa ficar **verde** (a branch `main` é protegida e não aceita merge sem ele); a coordenação revisa e mescla. Ninguém mescla o próprio PR.

Código não entra aqui: scripts, consultas e esquemas comuns, mapas e o modelo do livro são do [atlas-motor](https://github.com/youthmappers-ufv/atlas-motor). Uma melhoria que sirva a todos os municípios vira issue ou PR lá.

## Dados públicos

Este repositório é **público**: cada commit, branch, issue e pull request fica visível assim que é enviado, antes de qualquer revisão, e continua no histórico mesmo depois de apagado. Por isso:

- **Só entram dados públicos**: o que já é aberto (OSM, bases oficiais abertas) ou o que a equipe levantou para ser publicado no atlas.
- **Nunca entram:** nomes de moradores, informantes ou servidores; telefones, e-mails e endereços de pessoas; CPF, RG, matrícula; fotos de fichas e anotações de campo brutas. Telefone público de um estabelecimento vai para o OSM, não para cá.
- **Dados da Prefeitura que não são abertos** (cadastros internos) não entram; se precisar cruzá-los com o atlas, o cruzamento é feito fora e só o resultado agregado entra, conforme o termo de parceria.
- O validador acusa e-mail, CPF, telefone e colunas proibidas, e o gancho de pre-push o roda antes do envio. Se algo pessoal for enviado por engano, avise a coordenação na hora: tirar do histórico exige reescrevê-lo.
- Commits e PRs mostram o seu usuário do GitHub. Se não quiser expor o seu e-mail, use o endereço *noreply* do GitHub (*Settings* > *Emails*).

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
- Veja o resultado com `python ../atlas-motor/scripts/construir.py --previa`: abre o site no navegador e recarrega a cada texto salvo em `atlas/`. Mudou dados, `temas.toml` ou `atlas.toml`? Rode `construir.py` de novo (pode ser com a prévia aberta, em outro terminal). Para o site completo em arquivo, `--renderizar html`.

## 5. Identidade visual (`tema/`)

Sem `tema/_brand.yml`, o atlas usa a identidade do Programa Youthmappers UFV. Para usar a da prefeitura parceira (cores, fontes, logos no site e no PDF), siga o [tema/LEIAME.md](tema/LEIAME.md). O uso da marca da prefeitura depende de autorização dela, registrada no termo de parceria. O validador confere as cores, os logos citados e o formato real das imagens.

## 6. Atualizar o motor

Quando sair uma versão nova do atlas-motor: `python ../atlas-motor/scripts/atualizar_motor.py --versao vX.Y.Z` (troca no `atlas.toml` e nos workflows), num PR próprio, `[CONFIG] Motor vX.Y.Z`. Leia o `CHANGELOG.md` do motor antes.

## 7. Edições do atlas

A coordenação cria a tag (`git tag v1.0 && git push origin v1.0`) quando uma etapa se fecha. O workflow *Publicar atlas* gera site e PDF daquela versão, publica em `edicoes/v1.0/` e como versão principal (se `publicacao.hospedagem = "pages"`) e anexa o PDF a um release.
