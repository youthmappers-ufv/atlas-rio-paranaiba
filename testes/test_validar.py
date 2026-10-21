"""Testes do validador: cada teste planta um defeito numa CÓPIA do repositório
e confere que validar.py o acusa (e que o repositório limpo passa)."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

from validar import verificar  # noqa: E402

IGNORAR = shutil.ignore_patterns(".git", "_site", "_gerado", ".quarto", "__pycache__", ".venv")
LINHA_OK = "LC-2027-001,2027-02-10,educacao,E.E. Major Silvestre,confirmado,node/13188586822,,-19.19,-46.24,"


class ValidadorComDefeitosPlantados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._base = tempfile.TemporaryDirectory()
        cls.base = Path(cls._base.name) / "repo"
        shutil.copytree(RAIZ, cls.base, ignore=IGNORAR)

    @classmethod
    def tearDownClass(cls):
        cls._base.cleanup()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name) / "repo"
        shutil.copytree(self.base, self.raiz)

    def tearDown(self):
        self._tmp.cleanup()

    # ------------------------------------------------------------ utilidades
    def arq(self, rel: str) -> Path:
        return self.raiz / rel

    def acrescentar(self, rel: str, texto: str) -> None:
        with self.arq(rel).open("a", encoding="utf-8", newline="") as f:
            f.write(texto + "\n")

    def trocar(self, rel: str, antes: str, depois: str) -> None:
        conteudo = self.arq(rel).read_text(encoding="utf-8")
        self.assertIn(antes, conteudo, f"o teste espera encontrar {antes!r} em {rel}")
        self.arq(rel).write_text(conteudo.replace(antes, depois, 1), encoding="utf-8")

    def erros(self) -> list[str]:
        return verificar(self.raiz).erros

    def assertAcusa(self, trecho: str):
        erros = self.erros()
        self.assertTrue(any(trecho in e for e in erros), f"esperado erro com {trecho!r}; veio: {erros}")

    # ------------------------------------------------------------ casos
    def test_repositorio_limpo_passa(self):
        self.assertEqual(self.erros(), [])

    def test_linha_valida_de_campo_passa(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK)
        self.assertEqual(self.erros(), [], "id de nó do OSM com 11 dígitos não pode ser confundido com CPF")

    def test_email_em_dado_curado(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK[:-1] + "falar com fulano@exemplo.com")
        self.assertAcusa("contém um e-mail")

    def test_cpf_em_dado_curado(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK[:-1] + "responsável 123.456.789-09")
        self.assertAcusa("parece conter um CPF")

    def test_coluna_proibida(self):
        self.trocar("dados/curados/eventos-culturais.csv", "fonte,url", "fonte,email")
        self.assertAcusa("[curados] eventos-culturais.csv: colunas")

    def test_coordenada_fora_do_municipio(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK.replace("-19.19,-46.24", "-22.90,-43.20"))
        self.assertAcusa("fora da área do município")

    def test_valor_fora_da_lista(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK.replace(",confirmado,", ",talvez,"))
        self.assertAcusa("'situacao' = 'talvez'")

    def test_tema_inexistente(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK.replace(",educacao,", ",esportes,"))
        self.assertAcusa("não é tema de temas.toml")

    def test_chave_repetida(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK)
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK)
        self.assertAcusa("chave 'LC-2027-001' repetida")

    def test_data_invalida(self):
        self.acrescentar("dados/curados/levantamentos-campo.csv", LINHA_OK.replace("2027-02-10", "10/02/2027"))
        self.assertAcusa("não é data válido")

    def test_csv_sem_esquema(self):
        self.arq("dados/curados/sem-esquema.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        self.assertAcusa("sem-esquema.csv: sem esquema")

    def test_base_oficial_sem_licenca(self):
        pasta = self.arq("dados/oficiais/inep")
        pasta.mkdir(parents=True)
        (pasta / "escolas.csv").write_text("codigo,escola,lat,lon\n31000001,E.E. Teste,-19.19,-46.24\n", encoding="utf-8")
        (pasta / "fonte.toml").write_text(
            'nome = "Catálogo"\norgao = "INEP"\nurl = "https://x"\ndata_acesso = 2026-11-10\narquivo = "escolas.csv"\n'
            '[colunas]\nid = "codigo"\nnome = "escola"\nlat = "lat"\nlon = "lon"\n', encoding="utf-8")
        self.assertAcusa("falta 'licenca'")

    def test_base_oficial_com_coluna_errada(self):
        pasta = self.arq("dados/oficiais/inep")
        pasta.mkdir(parents=True)
        (pasta / "escolas.csv").write_text("codigo,escola,lat,lon\n", encoding="utf-8")
        (pasta / "fonte.toml").write_text(
            'nome = "Catálogo"\norgao = "INEP"\nurl = "https://x"\ndata_acesso = 2026-11-10\nlicenca = "x"\n'
            'arquivo = "escolas.csv"\n[colunas]\nid = "codigo"\nnome = "nome_escola"\nlat = "lat"\nlon = "lon"\n',
            encoding="utf-8")
        self.assertAcusa("coluna para 'nome' (nome_escola) não está no CSV")

    def test_consulta_inexistente(self):
        self.arq("consultas/saude.overpassql").unlink()
        self.assertAcusa("consulta inexistente: consultas/saude.overpassql")

    def test_consulta_sem_bbox(self):
        arq = self.arq("consultas/saude.overpassql")
        arq.write_text(arq.read_text(encoding="utf-8").replace("{{bbox}}", "-20,-47,-19,-46"), encoding="utf-8")
        self.assertAcusa("não usa {{bbox}}")

    def test_prancha_em_andamento_sem_arquivo(self):
        self.trocar("temas.toml", 'id = "saude"\nnumero = 4\ntitulo = "Saúde"\nsituacao = "planejado"',
                    'id = "saude"\nnumero = 4\ntitulo = "Saúde"\nsituacao = "em-andamento"')
        self.assertAcusa("falta atlas/pranchas/04-saude.qmd")
        self.assertAcusa("pranchas/04-saude.qmd não está nos capítulos")

    def test_prancha_listada_mas_planejada(self):
        self.trocar("temas.toml", 'titulo = "Educação"\nsituacao = "em-andamento"', 'titulo = "Educação"\nsituacao = "planejado"')
        self.assertAcusa("pranchas/03-educacao.qmd está em atlas/_quarto.yml")

    def test_geojson_com_feicao_repetida(self):
        arq = self.arq("dados/osm/educacao.geojson")
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados["features"].append(dados["features"][0])
        arq.write_text(json.dumps(dados), encoding="utf-8")
        self.assertAcusa("repetido")
        self.assertAcusa("mas retrato.json diz")

    def test_geojson_de_tema_desconhecido(self):
        shutil.copy2(self.arq("dados/osm/educacao.geojson"), self.arq("dados/osm/esportes.geojson"))
        self.assertAcusa("esportes.geojson: não corresponde a nenhum tema")

    def test_marcas_de_conflito(self):
        self.acrescentar("atlas/metodo.qmd", "<<<<<<< HEAD\nversão A\n=======\nversão B\n>>>>>>> outra")
        self.assertAcusa("marcas de conflito")

    def test_hashtag_sem_cerquilha(self):
        self.trocar("atlas.toml", 'projeto = "#ymufv-atlas"', 'projeto = "ymufv-atlas"')
        self.assertAcusa("hashtags.projeto")


if __name__ == "__main__":
    unittest.main()
