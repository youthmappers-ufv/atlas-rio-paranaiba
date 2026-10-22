# Tema do atlas (opcional)

Sem esta pasta (ou só com este LEIAME), o atlas usa o tema padrão do motor: a identidade do Programa Youthmappers UFV.

Para usar a identidade da prefeitura parceira, crie aqui um `_brand.yml` (formato do Quarto, https://posit-dev.github.io/brand-yml/) e ponha os logos ao lado, por exemplo em `marca/`. O mesmo arquivo vale para o site e para o PDF:

```yaml
meta:
  name: Prefeitura Municipal de ...      # aparece no cabeçalho do PDF
logo:
  images:                                # todos aparecem na capa do PDF, na ordem
    prefeitura: marca/prefeitura.png
    programa: marca/ymufv_logo.png       # logo do programa, já incluído no motor
  medium: prefeitura                     # logo do site
color:
  palette:
    verde: "#1B6E3A"
    amarelo: "#D9A400"
    terra: "#8A4B1F"
  primary: verde        # títulos, faixas, links
  secondary: terra      # segunda faixa da capa, números das listas
  tertiary: amarelo     # filetes e marcadores
  light: "#F3F6EF"      # fundos claros
  foreground: "#222222" # texto
  background: "#FFFFFF"
typography:
  fonts:
    - family: Source Sans 3
      source: google
  base: Source Sans 3
  headings:
    family: Source Sans 3
    weight: bold
    color: primary
```

- Cores em hexadecimal (`#RRGGBB`), diretamente ou pelo nome na paleta.
- Imagens em PNG (de preferência com fundo transparente), JPG, SVG ou PDF, com a extensão certa: o validador confere o formato real.
- Fonte que não estiver instalada no computador ou no GitHub cai numa reserva (Source Sans, TeX Gyre Heros).
- O uso da marca da prefeitura precisa de autorização dela, registrada no termo de parceria: o repositório é público.
- Depois de mudar o tema, rode `construir.py` de novo (a prévia não acompanha mudanças no tema).
