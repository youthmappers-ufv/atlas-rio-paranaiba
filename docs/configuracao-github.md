# Configuração do GitHub

Passo a passo, feito uma vez pelo coordenador. A organização `youthmappers-ufv` está no plano **gratuito**, o que explica dois pontos do desenho:

- repositório privado **não publica GitHub Pages**: por isso o site sai num repositório público separado, que só recebe o resultado gerado;
- repositório privado **não tem proteção de branch nem regras**: o CI roda em todo PR, mas não dá para bloquear o merge sem ele. A regra é combinada: só mesclar com *Verificar* verde e revisão do coordenador.

Se a organização obtiver o plano Team (há benefício para professores pelo GitHub Education), dá para ativar a proteção da `main` e exigir o *Verificar*; o restante não muda.

## 1. Repositório operacional (privado)

1. Crie `youthmappers-ufv/atlas-rio-paranaiba`, **privado**, vazio (sem README nem licença).
2. No computador, na pasta deste repositório: `git remote add origin https://github.com/youthmappers-ufv/atlas-rio-paranaiba.git` e `git push -u origin main`.
3. **Acesso só do coordenador e do estudante.**
   - Organização > *Settings* > *Member privileges* > *Base permissions*: **No permission**. Assim, outros membros não veem repositórios privados que não lhes forem dados. Confira se isso não afeta outros repositórios da organização.
   - Repositório > *Settings* > *Collaborators and teams*: adicione o estudante com papel **Write** (ele abre branches e PRs; quem mescla é o coordenador).
   - Lembrete: donos (*owners*) da organização sempre veem tudo. Mantenha como dono só o coordenador.
4. *Settings* > *Actions* > *General*:
   - *Workflow permissions*: **Read and write permissions**.
   - Marque **Allow GitHub Actions to create and approve pull requests** (para o PR mensal de dados).
5. *Settings* > *General*: deixe só **Allow merge commits** (preserva os commits pequenos, um por passo, de cada PR); marque *Automatically delete head branches*.

## 2. Repositório público de saída

1. Crie `youthmappers-ufv/atlas`, **público**, com um README dizendo que o conteúdo é gerado automaticamente a partir de um repositório privado e que correções vão para o mapa (OSM) ou para o programa.
2. Crie a branch `gh-pages` (pode ser vazia) e, em *Settings* > *Pages*, publique a partir de **gh-pages**, pasta `/ (root)`. O endereço será `https://youthmappers-ufv.github.io/atlas/`.
3. Ninguém edita esse repositório à mão; só o workflow *Publicar atlas* escreve nele.

## 3. Chave de publicação (deploy key)

O repositório privado escreve no público por uma chave SSH que só dá acesso a esse repositório.

```bash
ssh-keygen -t ed25519 -C "publicar atlas" -N "" -f atlas-publicacao
```

- Conteúdo de `atlas-publicacao.pub` → `youthmappers-ufv/atlas` > *Settings* > *Deploy keys* > *Add deploy key*, marcando **Allow write access**.
- Conteúdo de `atlas-publicacao` (chave privada) → `youthmappers-ufv/atlas-rio-paranaiba` > *Settings* > *Secrets and variables* > *Actions* > *New repository secret*, com o nome **`ATLAS_CHAVE_PUBLICACAO`**.
- Apague os dois arquivos do computador depois.

## 4. Primeira publicação

1. Na aba *Actions* do repositório privado, rode *Verificar* (deve ficar verde).
2. Rode *Publicar atlas* pelo botão: versão `main`, dados versionados, destino `principal`.
3. Confira `https://youthmappers-ufv.github.io/atlas/` (o Pages leva alguns minutos na primeira vez).

## 5. Ligação com o repositório de documentos

No `youthmappers-ufv-docs`, o README de `projetos/ext-atlas/` aponta para os dois repositórios. Lá fica a parte institucional (proposta, relatórios à UFV, bibliografia, divulgação, orientação do estudante); aqui, a operacional. Relatórios citam números do atlas pela **edição** (tag), para que sejam verificáveis.

## Custos

Repositórios privados do plano gratuito têm 2.000 minutos de Actions por mês. O uso previsto (verificação por PR, um retrato e duas publicações por mês) fica bem abaixo disso; a publicação com PDF é a mais demorada, por instalar o TinyTeX.
