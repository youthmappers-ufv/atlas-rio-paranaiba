"""Verifica a integridade do repositório do atlas (roda no CI em todo pull request).

Confere:
  - atlas.toml e temas.toml: campos obrigatórios, ids únicos, consultas existentes;
  - dados/osm: GeoJSON bem formado, ids únicos, coordenadas no município, contagens
    iguais às do retrato.json;
  - dados/oficiais/<base>/fonte.toml: órgão, URL, data de acesso, licença, arquivo e
    colunas declaradas presentes no CSV;
  - dados/curados/*.csv: cada arquivo tem esquema em dados/esquemas/ e o respeita
    (colunas, obrigatórias, tipos, valores, padrões, chave única, coordenadas);
  - nenhum CSV com dado pessoal aparente (e-mail, CPF) nem coluna proibida;
  - pranchas: cada tema fora de "planejado" tem atlas/pranchas/<nn>-<id>.qmd e está
    no atlas/_quarto.yml, e vice-versa;
  - arquivos de texto em UTF-8, sem marcas de conflito, nenhum arquivo acima de 25 MB.

Uso: python scripts/validar.py [--raiz CAMINHO]
Saída: lista de ERRO/AVISO; código 1 se houver erro.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

from comum import RAIZ_PADRAO, Tema, coordenadas, ler_csv, ler_toml

SITUACOES = {"planejado", "em-andamento", "publicado"}
RECORTES = {"municipio", "sede", "ambos"}
COLUNAS_PROIBIDAS = {"cpf", "rg", "email", "e-mail", "telefone_pessoal", "celular", "matricula", "endereco_residencial"}
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
# Só o CPF formatado: 11 dígitos seguidos não servem, pois identificadores de nós do OSM já têm 11 dígitos.
RE_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
RE_URL = re.compile(r"^https?://\S+$")
TIPOS = {"texto", "inteiro", "decimal", "data", "lista", "latitude", "longitude", "tema", "url"}
IGNORAR = {".git", "_site", "_gerado", ".quarto", "__pycache__", "_freeze", ".venv"}
LIMITE_BYTES = 25 * 1024 * 1024
MARGEM = 0.02            # graus de tolerância em torno da caixa do município


class Relatorio:
    def __init__(self) -> None:
        self.erros: list[str] = []
        self.avisos: list[str] = []

    def erro(self, msg: str) -> None:
        self.erros.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)


def dentro_caixa(lon: float, lat: float, bbox: list[float]) -> bool:
    s, o, n, l = bbox
    return s - MARGEM <= lat <= n + MARGEM and o - MARGEM <= lon <= l + MARGEM


# ---------------------------------------------------------------- Configuração
def verificar_config(raiz: Path, r: Relatorio) -> tuple[dict, list[Tema]]:
    try:
        config = ler_toml(raiz / "atlas.toml")
    except (OSError, tomllib.TOMLDecodeError) as e:
        r.erro(f"[config] atlas.toml ilegível: {e}")
        return {}, []
    for chave in ("nome", "ibge", "osm_relacao", "bbox", "sede_bbox"):
        if chave not in config.get("municipio", {}):
            r.erro(f"[config] atlas.toml: falta municipio.{chave}")
    for chave in ("programa", "projeto"):
        if not str(config.get("hashtags", {}).get(chave, "")).startswith("#"):
            r.erro(f"[config] atlas.toml: hashtags.{chave} ausente ou sem '#'")
    try:
        brutos = ler_toml(raiz / "temas.toml").get("tema", [])
    except (OSError, tomllib.TOMLDecodeError) as e:
        r.erro(f"[temas] temas.toml ilegível: {e}")
        return config, []
    temas, ids, numeros = [], set(), set()
    for i, t in enumerate(brutos, 1):
        faltam = {"id", "numero", "titulo", "situacao", "consulta", "referencia", "recorte"} - set(t)
        if faltam:
            r.erro(f"[temas] tema {i}: faltam campos {sorted(faltam)}")
            continue
        tema = Tema(**{k: t[k] for k in Tema.__dataclass_fields__})
        if tema.id in ids:
            r.erro(f"[temas] id repetido: {tema.id}")
        if tema.numero in numeros:
            r.erro(f"[temas] número de prancha repetido: {tema.numero}")
        ids.add(tema.id)
        numeros.add(tema.numero)
        if tema.situacao not in SITUACOES:
            r.erro(f"[temas] {tema.id}: situação '{tema.situacao}' (use {sorted(SITUACOES)})")
        if tema.recorte not in RECORTES:
            r.erro(f"[temas] {tema.id}: recorte '{tema.recorte}' (use {sorted(RECORTES)})")
        consulta = raiz / "consultas" / tema.consulta
        if not consulta.exists():
            r.erro(f"[temas] {tema.id}: consulta inexistente: consultas/{tema.consulta}")
        elif "{{bbox}}" not in consulta.read_text(encoding="utf-8"):
            r.erro(f"[temas] {tema.id}: a consulta não usa {{{{bbox}}}} (precisa ser restrita ao município)")
        if tema.referencia != "interno" and not (raiz / "dados" / "oficiais" / tema.referencia).is_dir():
            r.aviso(f"[temas] {tema.id}: base oficial '{tema.referencia}' ainda não carregada em dados/oficiais/")
        temas.append(tema)
    return config, temas


# ---------------------------------------------------------------- Dados do OSM
def verificar_osm(raiz: Path, config: dict, temas: list[Tema], r: Relatorio) -> None:
    pasta = raiz / "dados" / "osm"
    if not (pasta / "limite.geojson").exists():
        r.aviso("[osm] dados/osm/limite.geojson ausente: rode scripts/baixar_osm.py")
        return
    bbox = config.get("municipio", {}).get("bbox", [-90, -180, 90, 180])
    retrato = {}
    if (pasta / "retrato.json").exists():
        try:
            retrato = json.loads((pasta / "retrato.json").read_text(encoding="utf-8")).get("temas", {})
        except json.JSONDecodeError as e:
            r.erro(f"[osm] retrato.json ilegível: {e}")
    else:
        r.erro("[osm] falta dados/osm/retrato.json (gerado por scripts/baixar_osm.py)")
    conhecidos = {t.id for t in temas} | {"limite"}
    for arq in sorted(pasta.glob("*.geojson")):
        nome = arq.stem
        if nome not in conhecidos:
            r.erro(f"[osm] {arq.name}: não corresponde a nenhum tema de temas.toml")
            continue
        try:
            dados = json.loads(arq.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            r.erro(f"[osm] {arq.name}: JSON inválido ({e})")
            continue
        if dados.get("type") != "FeatureCollection":
            r.erro(f"[osm] {arq.name}: não é FeatureCollection")
            continue
        vistos = set()
        for i, f in enumerate(dados.get("features", []), 1):
            osm = f.get("properties", {}).get("osm", "")
            if not re.fullmatch(r"(node|way|relation)/\d+", osm):
                r.erro(f"[osm] {arq.name}: feição {i} sem identificador OSM válido")
            elif osm in vistos:
                r.erro(f"[osm] {arq.name}: {osm} repetido")
            vistos.add(osm)
            try:
                pts = coordenadas(f["geometry"])
            except (KeyError, ValueError, TypeError) as e:
                r.erro(f"[osm] {arq.name}: {osm or i}: geometria inválida ({e})")
                continue
            if nome != "limite" and f["geometry"]["type"] != "LineString" and not all(dentro_caixa(x, y, bbox) for x, y in pts):
                r.erro(f"[osm] {arq.name}: {osm} fora da área do município")
        if nome != "limite":
            esperado = retrato.get(nome, {}).get("feicoes")
            if esperado is None:
                r.erro(f"[osm] {arq.name}: tema ausente do retrato.json")
            elif esperado != len(dados.get("features", [])):
                r.erro(f"[osm] {arq.name}: {len(dados['features'])} feições, mas retrato.json diz {esperado}")


# ---------------------------------------------------------------- Bases oficiais
def verificar_oficiais(raiz: Path, config: dict, r: Relatorio) -> None:
    bbox = config.get("municipio", {}).get("bbox", [-90, -180, 90, 180])
    for pasta in sorted(p for p in (raiz / "dados" / "oficiais").glob("*") if p.is_dir()):
        fonte_arq = pasta / "fonte.toml"
        if not fonte_arq.exists():
            r.erro(f"[oficiais] {pasta.name}: falta fonte.toml")
            continue
        try:
            fonte = ler_toml(fonte_arq)
        except tomllib.TOMLDecodeError as e:
            r.erro(f"[oficiais] {pasta.name}/fonte.toml ilegível: {e}")
            continue
        for chave in ("nome", "orgao", "url", "data_acesso", "licenca", "arquivo"):
            if not str(fonte.get(chave, "")).strip():
                r.erro(f"[oficiais] {pasta.name}/fonte.toml: falta '{chave}'")
        try:
            date.fromisoformat(str(fonte.get("data_acesso", "")))
        except ValueError:
            r.erro(f"[oficiais] {pasta.name}/fonte.toml: data_acesso deve ser AAAA-MM-DD")
        arq = pasta / str(fonte.get("arquivo", ""))
        if not arq.is_file():
            r.erro(f"[oficiais] {pasta.name}: arquivo declarado não existe: {fonte.get('arquivo')}")
            continue
        try:
            cab, linhas = ler_csv(arq)
        except UnicodeDecodeError:
            r.erro(f"[oficiais] {pasta.name}/{arq.name}: não está em UTF-8")
            continue
        colunas = fonte.get("colunas", {})
        for papel in ("id", "nome", "lat", "lon"):
            if colunas.get(papel) not in cab:
                r.erro(f"[oficiais] {pasta.name}: coluna para '{papel}' ({colunas.get(papel)}) não está no CSV")
        if colunas.get("lat") in cab and colunas.get("lon") in cab:
            for n, linha in enumerate(linhas, 2):
                try:
                    lat, lon = float(linha[colunas["lat"]]), float(linha[colunas["lon"]])
                except (TypeError, ValueError):
                    continue                      # item sem coordenada: tratado na completude
                if not dentro_caixa(lon, lat, bbox):
                    r.aviso(f"[oficiais] {pasta.name}/{arq.name}:{n}: coordenada fora da área do município")
        verificar_dados_pessoais(f"oficiais/{pasta.name}/{arq.name}", cab, linhas, r)


# ---------------------------------------------------------------- Dados curados
def verificar_curados(raiz: Path, config: dict, temas: list[Tema], r: Relatorio) -> None:
    bbox = config.get("municipio", {}).get("bbox", [-90, -180, 90, 180])
    ids_temas = {t.id for t in temas}
    esquemas = {}
    for esq in sorted((raiz / "dados" / "esquemas").glob("*.toml")):
        try:
            e = ler_toml(esq)
        except tomllib.TOMLDecodeError as erro:
            r.erro(f"[esquemas] {esq.name} ilegível: {erro}")
            continue
        esquemas[e.get("arquivo", "")] = (esq.name, e)
        for c in e.get("coluna", []):
            if c.get("tipo") not in TIPOS:
                r.erro(f"[esquemas] {esq.name}: coluna {c.get('nome')} com tipo '{c.get('tipo')}' desconhecido")
    for arq in sorted((raiz / "dados" / "curados").glob("*.csv")):
        rot = f"curados/{arq.name}"
        if arq.name not in esquemas:
            r.erro(f"[curados] {arq.name}: sem esquema em dados/esquemas/ (campo arquivo = \"{arq.name}\")")
            continue
        _, esq = esquemas[arq.name]
        try:
            cab, linhas = ler_csv(arq)
        except UnicodeDecodeError:
            r.erro(f"[curados] {arq.name}: não está em UTF-8")
            continue
        definidas = [c["nome"] for c in esq.get("coluna", [])]
        if cab != definidas:
            r.erro(f"[curados] {arq.name}: colunas {cab} diferem do esquema {definidas}")
            continue
        chaves = set()
        for n, linha in enumerate(linhas, 2):
            for c in esq["coluna"]:
                valor = (linha.get(c["nome"]) or "").strip()
                if not valor:
                    if c.get("obrigatoria"):
                        r.erro(f"[curados] {arq.name}:{n}: '{c['nome']}' é obrigatória")
                    continue
                problema = checar_tipo(valor, c, ids_temas)
                if problema:
                    r.erro(f"[curados] {arq.name}:{n}: '{c['nome']}' {problema}")
            chave = (linha.get(esq.get("chave", "")) or "").strip()
            if chave:
                if chave in chaves:
                    r.erro(f"[curados] {arq.name}:{n}: chave '{chave}' repetida")
                chaves.add(chave)
            lat, lon = linha.get("lat", "").strip(), linha.get("lon", "").strip()
            if bool(lat) != bool(lon):
                r.erro(f"[curados] {arq.name}:{n}: informe lat e lon juntas")
            elif lat and lon:
                try:
                    if not dentro_caixa(float(lon), float(lat), bbox):
                        r.erro(f"[curados] {arq.name}:{n}: coordenada fora da área do município")
                except ValueError:
                    pass                          # já apontado pela checagem de tipo
        verificar_dados_pessoais(rot, cab, linhas, r)
    for nome, (esq_nome, _) in esquemas.items():
        if not (raiz / "dados" / "curados" / nome).exists():
            r.erro(f"[esquemas] {esq_nome}: arquivo {nome} não existe em dados/curados/")


def checar_tipo(valor: str, c: dict, ids_temas: set[str]) -> str | None:
    tipo = c.get("tipo")
    try:
        if tipo == "inteiro":
            v = int(valor)
            if "minimo" in c and v < c["minimo"] or "maximo" in c and v > c["maximo"]:
                return f"fora do intervalo {c.get('minimo')}–{c.get('maximo')}"
        elif tipo in ("decimal", "latitude", "longitude"):
            v = float(valor)
            if tipo == "latitude" and not -90 <= v <= 90 or tipo == "longitude" and not -180 <= v <= 180:
                return "fora do intervalo válido"
        elif tipo == "data":
            date.fromisoformat(valor)
        elif tipo == "lista" and valor not in c.get("valores", []):
            return f"= '{valor}' não está entre {c.get('valores')}"
        elif tipo == "tema" and valor not in ids_temas:
            return f"= '{valor}' não é tema de temas.toml"
        elif tipo == "url" and not RE_URL.match(valor):
            return "não é uma URL http(s)"
    except ValueError:
        return f"= '{valor}' não é {tipo} válido"
    if c.get("padrao") and not re.fullmatch(c["padrao"], valor):
        return f"= '{valor}' não segue o padrão {c['padrao']}"
    return None


def verificar_dados_pessoais(rot: str, cab: list[str], linhas: list[dict], r: Relatorio) -> None:
    for col in cab:
        if col.strip().lower() in COLUNAS_PROIBIDAS:
            r.erro(f"[lgpd] {rot}: coluna '{col}' não é permitida (dado pessoal)")
    for n, linha in enumerate(linhas, 2):
        for col, valor in linha.items():
            valor = valor or ""
            if RE_EMAIL.search(valor):
                r.erro(f"[lgpd] {rot}:{n}: '{col}' contém um e-mail")
            if RE_CPF.search(valor):
                r.erro(f"[lgpd] {rot}:{n}: '{col}' parece conter um CPF")


# ---------------------------------------------------------------- Pranchas
def verificar_pranchas(raiz: Path, temas: list[Tema], r: Relatorio) -> None:
    quarto = raiz / "atlas" / "_quarto.yml"
    if not quarto.exists():
        r.erro("[atlas] falta atlas/_quarto.yml")
        return
    listadas = set(re.findall(r"pranchas/([\w-]+\.qmd)", quarto.read_text(encoding="utf-8")))
    esperadas = {t.prancha for t in temas if t.situacao != "planejado"}
    for t in temas:
        if t.situacao != "planejado" and not (raiz / "atlas" / "pranchas" / t.prancha).exists():
            r.erro(f"[atlas] {t.id} está '{t.situacao}', mas falta atlas/pranchas/{t.prancha}")
    for p in sorted(esperadas - listadas):
        r.erro(f"[atlas] pranchas/{p} não está nos capítulos de atlas/_quarto.yml")
    for p in sorted(listadas - esperadas):
        r.erro(f"[atlas] pranchas/{p} está em atlas/_quarto.yml, mas o tema está 'planejado' ou não existe")


# ---------------------------------------------------------------- Arquivos
def verificar_arquivos(raiz: Path, r: Relatorio) -> None:
    textos = {".md", ".qmd", ".toml", ".csv", ".py", ".yml", ".yaml", ".json", ".geojson", ".overpassql", ".scss", ".txt"}
    for arq in raiz.rglob("*"):
        if not arq.is_file() or IGNORAR & set(arq.relative_to(raiz).parts):
            continue
        rel = arq.relative_to(raiz).as_posix()
        if arq.stat().st_size > LIMITE_BYTES:
            r.erro(f"[arquivos] {rel}: maior que 25 MB (use outra forma de armazenamento)")
        if arq.suffix.lower() in textos:
            try:
                texto = arq.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                r.erro(f"[arquivos] {rel}: não está em UTF-8")
                continue
            if re.search(r"^(<{7}|>{7})( |$)", texto, re.MULTILINE):
                r.erro(f"[arquivos] {rel}: marcas de conflito de merge")


def verificar(raiz: Path) -> Relatorio:
    r = Relatorio()
    config, temas = verificar_config(raiz, r)
    verificar_osm(raiz, config, temas, r)
    verificar_oficiais(raiz, config, r)
    verificar_curados(raiz, config, temas, r)
    verificar_pranchas(raiz, temas, r)
    verificar_arquivos(raiz, r)
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", type=Path, default=RAIZ_PADRAO)
    args = ap.parse_args()
    r = verificar(args.raiz.resolve())
    for m in r.erros:
        print(f"ERRO   {m}")
    for m in r.avisos:
        print(f"AVISO  {m}")
    print(f"\n{len(r.erros)} erro(s), {len(r.avisos)} aviso(s).")
    return 1 if r.erros else 0


if __name__ == "__main__":
    sys.exit(main())
