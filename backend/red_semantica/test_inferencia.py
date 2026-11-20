import unittest

import networkx as nx

from inferencia import VOC, construir_rdf, inferir_afinidades


class InferenciaTest(unittest.TestCase):
    def setUp(self):
        self.grafo = nx.DiGraph()
        self.grafo.add_nodes_from(("Alumno", "Bloque/Aptitud", "Carrera"), tipo="clase")
        self.grafo.add_node("a1", tipo="instancia", nombre="Ana", no_control="123")
        self.grafo.add_node("b1", tipo="instancia", nombre="Calculo")
        self.grafo.add_node("b2", tipo="instancia", nombre="Situacion socioeconomica")
        self.grafo.add_node("c1", tipo="instancia", nombre="Ingenieria")
        self.grafo.add_node("c2", tipo="instancia", nombre="Otra carrera")
        for instancia, clase in (("a1", "Alumno"), ("b1", "Bloque/Aptitud"),
                                 ("b2", "Bloque/Aptitud"), ("c1", "Carrera"),
                                 ("c2", "Carrera")):
            self.grafo.add_edge(instancia, clase)
        self.grafo.add_edge("a1", "b1", label="evaluado", puntaje=85)
        self.grafo.add_edge("a1", "b2", label="evaluado", puntaje=99)
        self.grafo.add_edge("b1", "c1", label="importante para")
        self.grafo.add_edge("b2", "c2", label="importante para")
        self.grafo.add_edge("a1", "c2", label="carrera sugerida")

    def test_owl_rl_deduce_una_afinidad_y_excluye_la_socioeconomia(self):
        rdf = construir_rdf(self.grafo)
        self.assertNotIn((VOC.a1, VOC.afinidadCon, VOC.c1), rdf)

        resultados = inferir_afinidades(self.grafo)
        self.assertEqual([(r.alumno_id, r.carrera_id) for r in resultados], [("a1", "c1")])
        self.assertEqual([(e.bloque, e.puntaje) for e in resultados[0].evidencias],
                         [("Calculo", 85)])

    def test_puntaje_bajo_no_produce_afinidad(self):
        self.grafo.edges["a1", "b1"]["puntaje"] = 84
        self.assertEqual(inferir_afinidades(self.grafo), [])


if __name__ == "__main__":
    unittest.main()
