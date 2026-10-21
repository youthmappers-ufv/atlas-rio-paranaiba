"""Baixa do OpenStreetMap (Overpass) o retrato dos dados do atlas.

Grava em dados/osm/:
  limite.geojson      limite municipal (relação de atlas.toml)
  <tema>.geojson      objetos de cada tema, recortados pelo limite
  retrato.json        data da base do OSM, servidor, contagens e impressão digital das consultas

Os arquivos são ordenados e as coordenadas arredondadas (7 casas, ~1 cm), para
que cada atualização produza diferenças legíveis no Git.

Uso:
  python scripts/baixar_osm.py                 # todos os temas
  python scripts/baixar_osm.py --tema educacao # só um tema (o retrato é atualizado só nele)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from comum import (RAIZ_PADRAO, aneis_externos, dentro, escrever_json, ler_config, ler_temas,
                   ponto_representativo)

USER_AGENT = "atlas-rio-paranaiba (Programa Youthmappers UFV)"
CHAVES_AREA = ("building", "landuse", "leisure", "natural", "amenity", "place", "tourism",
               "historic", "healthcare", "office", "area")


def consultar(config: dict, corpo: str) -> tuple[dict, str]:
    # "out geom" traz etiquetas, membros e geometria ("out tags geom" omitiria os membros das relações)
    consulta = f"[out:json][timeout:{config['overpass']['tempo_limite']}];{corpo}out geom;"
    dados = urllib.parse.urlencode({"data": consulta}).encode()
    erros = []
    for url in config["overpass"]["servidores"]:
        try:
            req = urllib.request.Request(url, data=dados, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=config["overpass"]["tempo_limite"] + 30) as r:
                return json.load(r), url
        except Exception as erro:               # servidor fora do ar ou sobrecarregado: tenta o próximo
            erros.append(f"{url}: {erro}")
            time.sleep(3)
    raise RuntimeError("nenhum servidor Overpass respondeu:\n  " + "\n  ".join(erros))


def r7(v: float) -> float:
    return round(v, 7)


def geometria(e: dict) -> dict | None:
    if e["type"] == "node":
        return {"type": "Point", "coordinates": [r7(e["lon"]), r7(e["lat"])]}
    if e["type"] == "way" and e.get("geometry"):
        pts = [[r7(p["lon"]), r7(p["lat"])] for p in e["geometry"] if p]
        tags = e.get("tags", {})
        fechado = len(pts) >= 4 and pts[0] == pts[-1]
        linear = "highway" in tags or "waterway" in tags or tags.get("area") == "no"
        if fechado and (not linear or tags.get("area") == "yes") and any(k in tags for k in CHAVES_AREA):
            return {"type": "Polygon", "coordinates": [pts]}
        return {"type": "LineString", "coordinates": pts}
    if e["type"] == "relation":
        pts = [(p["lon"], p["lat"]) for m in e.get("members", []) for p in (m.get("geometry") or []) if p]
        if pts:                                  # relação: guardamos o centro da caixa envolvente
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            return {"type": "Point", "coordinates": [r7((min(xs) + max(xs)) / 2), r7((min(ys) + max(ys)) / 2)]}
    return None


def feicoes(bruto: dict, aneis: list) -> list[dict]:
    saida = {}
    for e in bruto["elements"]:
        g = geometria(e)
        if g is None:
            continue
        lon, lat = ponto_representativo(g)
        if g["type"] == "LineString":            # via ou rio: basta um vértice dentro do município
            if not any(dentro(x, y, aneis) for x, y in g["coordinates"]):
                continue
        elif not dentro(lon, lat, aneis):
            continue
        osm = f"{e['type']}/{e['id']}"
        saida[osm] = {"type": "Feature", "properties": {"osm": osm, "tags": dict(sorted(e.get("tags", {}).items()))},
                      "geometry": g}
    tipo = {"node": 0, "way": 1, "relation": 2}
    return sorted(saida.values(), key=lambda f: (tipo[f["properties"]["osm"].split("/")[0]],
                                                 int(f["properties"]["osm"].split("/")[1])))


def gravar_geojson(arquivo: Path, lista: list[dict]) -> None:
    # Uma feição por linha: diffs do Git mostram exatamente o que mudou.
    linhas = ",\n".join(json.dumps(f, ensure_ascii=False, separators=(",", ":")) for f in lista)
    arquivo.write_text('{"type":"FeatureCollection","features":[\n' + linhas + "\n]}\n", encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tema", action="append", help="baixar só este tema (pode repetir)")
    ap.add_argument("--raiz", type=Path, default=RAIZ_PADRAO)
    args = ap.parse_args()
    config, temas = ler_config(args.raiz), ler_temas(args.raiz)
    pasta = args.raiz / "dados" / "osm"
    pasta.mkdir(parents=True, exist_ok=True)
    escolhidos = [t for t in temas if not args.tema or t.id in args.tema]
    if args.tema and len(escolhidos) != len(args.tema):
        print(f"Tema desconhecido: {set(args.tema) - {t.id for t in temas}}", file=sys.stderr)
        return 2

    retrato_arq = pasta / "retrato.json"
    retrato = json.loads(retrato_arq.read_text(encoding="utf-8")) if retrato_arq.exists() else {"temas": {}}

    print("Limite municipal...")
    bruto, servidor = consultar(config, f"rel({config['municipio']['osm_relacao']});")
    relacao = next(e for e in bruto["elements"] if e["type"] == "relation")
    aneis = [[[r7(x), r7(y)] for x, y in anel] for anel in aneis_externos(relacao)]
    if not aneis or any(a[0] != a[-1] for a in aneis):
        print("Limite municipal incompleto (anel aberto); nada foi gravado.", file=sys.stderr)
        return 1
    gravar_geojson(pasta / "limite.geojson", [{
        "type": "Feature", "geometry": {"type": "Polygon", "coordinates": aneis},
        "properties": {"osm": f"relation/{relacao['id']}", "tags": dict(sorted(relacao.get("tags", {}).items()))}}])
    base_osm = bruto.get("osm3s", {}).get("timestamp_osm_base", "")

    s, o, n, l = config["municipio"]["bbox"]
    for t in escolhidos:
        corpo = (args.raiz / "consultas" / t.consulta).read_text(encoding="utf-8")
        corpo_sem_comentarios = "\n".join(x for x in corpo.splitlines() if not x.strip().startswith("//"))
        print(f"{t.id}...", end=" ", flush=True)
        bruto, servidor = consultar(config, corpo_sem_comentarios.replace("{{bbox}}", f"{s},{o},{n},{l}"))
        lista = feicoes(bruto, aneis)
        gravar_geojson(pasta / f"{t.id}.geojson", lista)
        retrato["temas"][t.id] = {"feicoes": len(lista),
                                   "consulta_sha256": hashlib.sha256(corpo.encode()).hexdigest()[:16],
                                   "base_osm": bruto.get("osm3s", {}).get("timestamp_osm_base", base_osm)}
        print(len(lista))
    retrato.update({"gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "servidor": servidor, "base_osm": base_osm,
                    "municipio": config["municipio"]["nome"], "relacao": config["municipio"]["osm_relacao"]})
    escrever_json(retrato_arq, retrato)
    print(f"Retrato gravado em {retrato_arq.relative_to(args.raiz)} (base do OSM: {base_osm}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
