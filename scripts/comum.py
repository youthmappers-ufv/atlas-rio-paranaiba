"""Funções comuns aos scripts do atlas: configuração, geometria e nomes.

Só biblioteca padrão (Python 3.11+), para que a verificação do CI rode sem
instalar nada. O que precisa de bibliotecas externas (mapas) fica em mapas.py.
"""
from __future__ import annotations

import csv
import json
import math
import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- Configuração
@dataclass
class Tema:
    id: str
    numero: int
    titulo: str
    situacao: str
    consulta: str
    referencia: str
    recorte: str

    @property
    def prancha(self) -> str:
        return f"{self.numero:02d}-{self.id}.qmd"


def ler_toml(arquivo: Path) -> dict:
    with arquivo.open("rb") as f:
        return tomllib.load(f)


def ler_config(raiz: Path = RAIZ_PADRAO) -> dict:
    return ler_toml(raiz / "atlas.toml")


def ler_temas(raiz: Path = RAIZ_PADRAO) -> list[Tema]:
    dados = ler_toml(raiz / "temas.toml")
    return [Tema(**t) for t in dados.get("tema", [])]


def ler_csv(arquivo: Path) -> tuple[list[str], list[dict]]:
    with arquivo.open(encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        linhas = list(leitor)
        return list(leitor.fieldnames or []), linhas


def escrever_json(arquivo: Path, dados) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- Geometria
def aneis_externos(relacao: dict) -> list[list[tuple[float, float]]]:
    """Junta os caminhos 'outer' de uma relação do Overpass (out geom) em anéis (lon, lat)."""
    pedacos = [[(p["lon"], p["lat"]) for p in m["geometry"]]
               for m in relacao.get("members", []) if m.get("type") == "way" and m.get("role") == "outer"]
    aneis = []
    while pedacos:
        anel = pedacos.pop(0)
        while anel[0] != anel[-1]:
            for i, p in enumerate(pedacos):
                if p[0] == anel[-1]:
                    anel += p[1:]
                elif p[-1] == anel[-1]:
                    anel += p[-2::-1]
                else:
                    continue
                pedacos.pop(i)
                break
            else:
                break                     # anel aberto: dados incompletos
        aneis.append(anel)
    return aneis


def dentro(lon: float, lat: float, aneis: list) -> bool:
    """Ponto no polígono (par-ímpar), para um ou mais anéis."""
    res = False
    for anel in aneis:
        for (x1, y1), (x2, y2) in zip(anel, anel[1:]):
            if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
                res = not res
    return res


def distancia_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Distância em metros (haversine)."""
    r = 6371008.8
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df, dl = f2 - f1, math.radians(lon2 - lon1)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def coordenadas(geometria: dict) -> list[tuple[float, float]]:
    """Todos os vértices de uma geometria GeoJSON (Point, LineString, Polygon)."""
    t, c = geometria["type"], geometria["coordinates"]
    if t == "Point":
        return [tuple(c)]
    if t == "LineString":
        return [tuple(p) for p in c]
    if t == "Polygon":
        return [tuple(p) for anel in c for p in anel]
    raise ValueError(f"geometria não suportada: {t}")


def ponto_representativo(geometria: dict) -> tuple[float, float]:
    pts = coordenadas(geometria)
    if geometria["type"] == "LineString":
        return pts[len(pts) // 2]
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def ler_limite(raiz: Path = RAIZ_PADRAO) -> list[list[tuple[float, float]]]:
    dados = json.loads((raiz / "dados" / "osm" / "limite.geojson").read_text(encoding="utf-8"))
    geometria = dados["features"][0]["geometry"]
    return [[tuple(p) for p in anel] for anel in geometria["coordinates"]]


# ---------------------------------------------------------------- Nomes
ABREVIACOES = {
    r"\be\.?\s*e\.?\b": "escola estadual",
    r"\be\.?\s*m\.?\b": "escola municipal",
    r"\bemef\b": "escola municipal de ensino fundamental",
    r"\bcmei\b": "centro municipal de educacao infantil",
    r"\bprof\.?\b": "professor",
    r"\bprofa\.?\b": "professora",
    r"\bdr\.?\b": "doutor",
    r"\bubs\b": "unidade basica de saude",
    r"\besf\b": "estrategia saude da familia",
    r"\bsta\.?\b": "santa",
    r"\bsto\.?\b": "santo",
    r"\bn\.?\s*s(ra)?\.?\b": "nossa senhora",
}


def normalizar_nome(nome: str) -> str:
    """Minúsculas, sem acentos e com as abreviações usuais expandidas."""
    t = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    for padrao, troca in ABREVIACOES.items():
        t = re.sub(padrao, troca, t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()
