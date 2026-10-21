"""Testes da normalização de nomes e da correspondência OSM × base oficial."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from comum import dentro, distancia_m, normalizar_nome  # noqa: E402
from indicadores import correspondencias  # noqa: E402


def feicao(nome: str, lon: float, lat: float) -> dict:
    return {"geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {"tags": {"name": nome}}}


class Nomes(unittest.TestCase):
    def test_abreviacoes_e_acentos(self):
        self.assertEqual(normalizar_nome("E.E. Prof. João Gonçalves"), "escola estadual professor joao goncalves")
        self.assertEqual(normalizar_nome("UBS Centro"), "unidade basica de saude centro")
        self.assertEqual(normalizar_nome("Igreja N. Sra. do Rosário"), "igreja nossa senhora do rosario")


class Correspondencia(unittest.TestCase):
    LON, LAT = -46.2411, -19.1965
    D100 = 100 / 111320          # ~100 m em latitude

    def test_mesmo_item_perto_e_nome_parecido(self):
        o = [{"nome": "EE Major Silvestre", "lon": self.LON, "lat": self.LAT}]
        f = [feicao("Escola Estadual Major Silvestre", self.LON, self.LAT + self.D100)]
        self.assertEqual(len(correspondencias(o, f, 150, 0.6)), 1)

    def test_longe_demais(self):
        o = [{"nome": "EE Major Silvestre", "lon": self.LON, "lat": self.LAT}]
        f = [feicao("Escola Estadual Major Silvestre", self.LON, self.LAT + 2 * self.D100)]
        self.assertEqual(correspondencias(o, f, 150, 0.6), [])

    def test_nome_diferente(self):
        o = [{"nome": "EE Major Silvestre", "lon": self.LON, "lat": self.LAT}]
        f = [feicao("Creche Municipal Maria Mãe de Deus", self.LON, self.LAT)]
        self.assertEqual(correspondencias(o, f, 150, 0.6), [])

    def test_um_para_um(self):
        o = [{"nome": "EE Major Silvestre", "lon": self.LON, "lat": self.LAT},
             {"nome": "E.E. Major Silvestre", "lon": self.LON, "lat": self.LAT}]
        f = [feicao("Escola Estadual Major Silvestre", self.LON, self.LAT)]
        self.assertEqual(len(correspondencias(o, f, 150, 0.6)), 1)

    def test_item_sem_coordenada_nao_corresponde(self):
        o = [{"nome": "EE Major Silvestre", "lon": None, "lat": None}]
        f = [feicao("Escola Estadual Major Silvestre", self.LON, self.LAT)]
        self.assertEqual(correspondencias(o, f, 150, 0.6), [])


class Geometria(unittest.TestCase):
    def test_distancia(self):
        self.assertAlmostEqual(distancia_m(-46.0, -19.0, -46.0, -19.01), 1112, delta=3)

    def test_ponto_no_poligono(self):
        quadrado = [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
        self.assertTrue(dentro(0.5, 0.5, quadrado))
        self.assertFalse(dentro(1.5, 0.5, quadrado))


if __name__ == "__main__":
    unittest.main()
