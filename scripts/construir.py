"""Prepara o atlas para o Quarto: valida, calcula indicadores, gera mapas e os
trechos em Markdown que as pranchas incluem (atlas/_gerado/, fora do Git).

Uso:
  python scripts/construir.py              # com os dados versionados em dados/osm/
  python scripts/construir.py --baixar     # baixa um retrato novo do OSM antes
  python scripts/construir.py --sem-mapas  # sem matplotlib (só indicadores e textos)
Depois: quarto render atlas            (site e PDF em atlas/_site/)

A versão mostrada no atlas vem da variável ATLAS_VERSAO (o CI usa a tag ou o
commit); sem ela, usa "desenvolvimento".
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from comum import RAIZ_PADRAO, ler_config, ler_temas
from indicadores import calcular
from validar import verificar


def tabela(linhas: list[tuple[str, str]]) -> str:
    corpo = "\n".join(f"| {a} | {b} |" for a, b in linhas)
    return f"| Indicador | Valor |\n|:--|--:|\n{corpo}\n"


def trecho_tema(tema, res: dict, figuras: list[tuple[str, str]], retrato: dict, config: dict) -> str:
    partes = []
    for arq, legenda in figuras:
        partes.append(f"![{legenda}](../_gerado/figuras/{arq}){{fig-alt=\"{legenda}\" width=100%}}\n")
    partes.append("Pontos cheios: objetos com nome no mapa; pontos vazados: sem nome.\n")
    partes.append(tabela(res["linhas"]))
    lacunas = res.get("lacunas") or []
    if lacunas:
        partes.append(f"\n**Itens da base oficial sem correspondente no mapa** ({len(lacunas)}):\n")
        partes.append("| Código | Nome |\n|:--|:--|\n" + "\n".join(f"| {o['id']} | {o['nome']} |" for o in lacunas[:60]) + "\n")
        if len(lacunas) > 60:
            partes.append(f"\n… e mais {len(lacunas) - 60}; lista completa nos dados para download.\n")
    base = retrato.get("temas", {}).get(tema.id, {}).get("base_osm") or retrato.get("base_osm", "")
    partes.append(f"\n*Fonte: OpenStreetMap, dados de {base[:10] or 'data desconhecida'}. "
                  f"{config['publicacao']['atribuicao']}.*\n")
    return "\n".join(partes)


def versao(raiz: Path) -> str:
    if os.environ.get("ATLAS_VERSAO"):
        return os.environ["ATLAS_VERSAO"]
    try:
        return subprocess.run(["git", "describe", "--tags", "--always", "--dirty"], cwd=raiz,
                              capture_output=True, text=True, check=True).stdout.strip() or "desenvolvimento"
    except (OSError, subprocess.CalledProcessError):
        return "desenvolvimento"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baixar", action="store_true", help="baixar um retrato novo do OSM antes")
    ap.add_argument("--sem-mapas", action="store_true", help="não gerar mapas (sem matplotlib)")
    ap.add_argument("--raiz", type=Path, default=RAIZ_PADRAO)
    args = ap.parse_args()
    raiz = args.raiz.resolve()

    if args.baixar:
        if subprocess.run([sys.executable, str(raiz / "scripts" / "baixar_osm.py"), "--raiz", str(raiz)]).returncode:
            return 1
    r = verificar(raiz)
    if r.erros:
        print("A validação encontrou erros; corrija antes de construir:\n  " + "\n  ".join(r.erros), file=sys.stderr)
        return 1

    config, temas = ler_config(raiz), ler_temas(raiz)
    gerado = raiz / "atlas" / "_gerado"
    if gerado.exists():
        shutil.rmtree(gerado)
    (gerado / "downloads").mkdir(parents=True)
    retrato_arq = raiz / "dados" / "osm" / "retrato.json"
    retrato = json.loads(retrato_arq.read_text(encoding="utf-8")) if retrato_arq.exists() else {}

    desenhar = None
    if not args.sem_mapas:
        from mapas import desenhar                # importa o matplotlib só aqui

    resumo = []
    for t in temas:
        if t.situacao == "planejado":
            continue
        res = calcular(raiz, t, config)
        figuras = []
        if desenhar:
            for rec in (("municipio", "sede") if t.recorte == "ambos" else (t.recorte,)):
                arq = f"{t.id}-{rec}.png"
                desenhar(raiz, t, rec, config, gerado / "figuras" / arq)
                figuras.append((arq, f"{t.titulo}: {'sede do município' if rec == 'sede' else 'município'}"))
        (gerado / f"{t.id}.md").write_text(trecho_tema(t, res, figuras, retrato, config), encoding="utf-8")
        origem = raiz / "dados" / "osm" / f"{t.id}.geojson"
        if origem.exists():
            shutil.copy2(origem, gerado / "downloads" / origem.name)
        resumo.append((t, res))
        print(f"{t.numero:>2}. {t.titulo}: {res['total']} objetos")

    linhas = "\n".join(f"| {t.numero} | [{t.titulo}](pranchas/{t.prancha.replace('.qmd', '.html')}) | {res['total']} |"
                       for t, res in resumo)
    (gerado / "pranchas.md").write_text("| Nº | Prancha | Objetos no mapa |\n|--:|:--|--:|\n" + linhas + "\n", encoding="utf-8")
    shutil.copy2(raiz / "dados" / "osm" / "limite.geojson", gerado / "downloads" / "limite.geojson")
    itens = ["- [Limite do município](_gerado/downloads/limite.geojson)"] + [
        f"- [{t.titulo}](_gerado/downloads/{t.id}.geojson)" for t, _ in resumo
        if (gerado / "downloads" / f"{t.id}.geojson").exists()]
    (gerado / "downloads.md").write_text("\n".join(itens) + "\n", encoding="utf-8")
    (gerado / "edicao.md").write_text(
        f"Versão **{versao(raiz)}**, com dados do OpenStreetMap de **{retrato.get('base_osm', '')[:10] or 'data desconhecida'}**.\n",
        encoding="utf-8")
    print(f"Pronto: {gerado.relative_to(raiz)}. Agora: quarto render atlas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
