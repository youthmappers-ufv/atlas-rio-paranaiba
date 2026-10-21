"""Mapas das pranchas (PNG), com layout cartográfico: limite, objetos do tema,
escala, norte e atribuição. Precisa do matplotlib (pip install matplotlib).

Usado por construir.py; direto: python scripts/mapas.py --tema educacao
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from comum import RAIZ_PADRAO, Tema, ler_config, ler_limite, ler_temas  # noqa: E402
from indicadores import ler_feicoes  # noqa: E402

AZUL, BORDO, DOURADO, CINZA, CLARO = "#304068", "#7A1C1C", "#BC9C38", "#303030", "#F4F1E8"
COR_TEMA = {"localizacao": BORDO, "sistema-viario": CINZA, "educacao": AZUL, "saude": BORDO,
            "equipamentos": AZUL, "meio-ambiente": "#2E7D32", "mobilidade": DOURADO,
            "area-rural": "#6D4C41", "cultura-turismo": BORDO}


def caixa(recorte: str, config: dict) -> tuple[float, float, float, float]:
    return tuple(config["municipio"]["sede_bbox" if recorte == "sede" else "bbox"])


def desenhar(raiz: Path, tema: Tema, recorte: str, config: dict, saida: Path) -> Path:
    s, o, n, l = caixa(recorte, config)
    fx = math.cos(math.radians((s + n) / 2))
    largura = 7.0
    altura = largura * (n - s) / ((l - o) * fx)
    fig, ax = plt.subplots(figsize=(largura, altura), dpi=200)
    ax.set_xlim(o, l)
    ax.set_ylim(s, n)
    ax.set_aspect(1 / fx)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    ax.add_patch(plt.Rectangle((o, s), l - o, n - s, color="#FFFFFF", zorder=0))

    for anel in ler_limite(raiz):
        xs, ys = zip(*anel)
        ax.fill(xs, ys, color=CLARO, zorder=1)
        ax.plot(xs, ys, color=BORDO, lw=1.2, ls=(0, (5, 2)), zorder=6)

    # fundo de referência: vias (do retrato do sistema viário) e, no município, nomes das localidades
    if tema.id not in ("sistema-viario", "area-rural"):
        for f in ler_feicoes(raiz, "sistema-viario"):
            g, hw = f["geometry"], f["properties"]["tags"].get("highway", "")
            if g["type"] != "LineString" or (recorte != "sede" and not hw.startswith(
                    ("trunk", "primary", "secondary", "tertiary", "unclassified"))):
                continue
            xs, ys = zip(*g["coordinates"])
            ax.plot(xs, ys, color="#C9C9C9", lw=0.9 if recorte == "sede" else 0.35, zorder=1.5)
    if recorte != "sede":
        for f in ler_feicoes(raiz, "localizacao"):
            nome = f["properties"]["tags"].get("name")
            if nome and f["geometry"]["type"] == "Point":
                x, y = f["geometry"]["coordinates"]
                ax.text(x, y + (n - s) * 0.012, nome, ha="center", va="bottom", fontsize=6.5, color=CINZA,
                        style="italic", zorder=8)

    cor = COR_TEMA.get(tema.id, AZUL)
    pontos_x, pontos_y, vazios_x, vazios_y = [], [], [], []
    for f in ler_feicoes(raiz, tema.id):
        g, tags = f["geometry"], f["properties"]["tags"]
        if g["type"] == "LineString":
            xs, ys = zip(*g["coordinates"])
            if "waterway" in tags:
                ax.plot(xs, ys, color="#3A7BD5", lw=0.7, zorder=2)
            else:
                principal = tags.get("highway", "").startswith(("trunk", "primary", "secondary"))
                ax.plot(xs, ys, color=cor if tema.id in ("sistema-viario", "area-rural") else "#9E9E9E",
                        lw=1.1 if principal else 0.4, zorder=3)
        elif g["type"] == "Polygon":
            xs, ys = zip(*g["coordinates"][0])
            ax.fill(xs, ys, color=cor, alpha=0.35, lw=0, zorder=2)
            cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
            (pontos_x if tags.get("name") else vazios_x).append(cx)
            (pontos_y if tags.get("name") else vazios_y).append(cy)
        else:
            x, y = g["coordinates"]
            (pontos_x if tags.get("name") else vazios_x).append(x)
            (pontos_y if tags.get("name") else vazios_y).append(y)
    ax.scatter(pontos_x, pontos_y, s=22, color=cor, edgecolors="white", linewidths=0.6, zorder=5)
    ax.scatter(vazios_x, vazios_y, s=14, facecolors="white", edgecolors=cor, linewidths=0.9, zorder=5)

    # escala (0,5 km na sede, 5 km no município), norte e atribuição
    km = 0.5 if recorte == "sede" else 5
    dx = km / (111.32 * fx)
    x0, y0 = o + (l - o) * 0.04, s + (n - s) * 0.04
    ax.plot([x0, x0 + dx], [y0, y0], color=CINZA, lw=2, zorder=7)
    ax.text(x0 + dx / 2, y0 + (n - s) * 0.012, f"{km:g} km".replace(".", ","), ha="center", va="bottom",
            fontsize=7, color=CINZA, zorder=7)
    ax.annotate("N", xy=(l - (l - o) * 0.04, n - (n - s) * 0.04), xytext=(l - (l - o) * 0.04, n - (n - s) * 0.12),
                ha="center", fontsize=9, fontweight="bold", color=CINZA,
                arrowprops=dict(arrowstyle="-|>", color=CINZA, lw=1.2), zorder=7)
    ax.text(l - (l - o) * 0.01, s + (n - s) * 0.01, config["publicacao"]["atribuicao"], ha="right", va="bottom",
            fontsize=5.5, color="#666666", zorder=7)

    saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, dpi=200)
    plt.close(fig)
    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tema", action="append")
    ap.add_argument("--raiz", type=Path, default=RAIZ_PADRAO)
    args = ap.parse_args()
    config = ler_config(args.raiz)
    for t in ler_temas(args.raiz):
        if args.tema and t.id not in args.tema:
            continue
        for rec in (("municipio", "sede") if t.recorte == "ambos" else (t.recorte,)):
            arq = desenhar(args.raiz, t, rec, config, args.raiz / "atlas" / "_gerado" / "figuras" / f"{t.id}-{rec}.png")
            print(arq.relative_to(args.raiz))
    return 0


if __name__ == "__main__":
    sys.exit(main())
