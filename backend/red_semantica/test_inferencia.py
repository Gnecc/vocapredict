import unittest

import networkx as nx

from criterio import AgenteIntereses
from inferencia import VOC, construir_rdf, inferir_afinidades


class InferenciaTest(unittest.TestCase):
    def test_selector_respeta_empates_y_excluye_socioeconomia(self):
        seleccion = AgenteIntereses().seleccionar({
            "b10": 1, "b1": 0.9, "b2": 0.8, "b3": 0.8, "b4": 0.69,
        })
        self.assertEqual(seleccion, ("b1", "b2", "b3"))
        self.assertEqual(AgenteIntereses().seleccionar({"b1": 0.70, "b2": 0.69}),
                         ("b1",))
        self.assertEqual(AgenteIntereses().seleccionar({"b10": 1}), ())

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
        self.grafo.add_edge("b1", "c1", label="perfil de referencia")
        self.grafo.add_edge("b2", "c2", label="perfil de referencia")
        self.grafo.add_edge("a1", "c2", label="carrera sugerida")

    def test_owl_rl_deduce_conexion_y_excluye_la_socioeconomia(self):
        rdf = construir_rdf(self.grafo)
        self.assertNotIn((VOC.a1, VOC.conexionExploratoria, VOC.c1), rdf)

        resultados = inferir_afinidades(self.grafo)
        self.assertEqual([(r.alumno_id, r.carrera_id) for r in resultados], [("a1", "c1")])
        self.assertEqual([(e.bloque, e.puntaje) for e in resultados[0].evidencias],
                         [("Calculo", 85)])

    def test_puntaje_bajo_no_produce_conexion(self):
        self.grafo.edges["a1", "b1"]["puntaje"] = 69
        self.assertEqual(inferir_afinidades(self.grafo), [])

    def test_maximo_dos_intereses_y_varias_carreras(self):
        for bloque, puntaje in (("b3", 90), ("b4", 88)):
            self.grafo.add_node(bloque, tipo="instancia", nombre=bloque)
            self.grafo.add_edge(bloque, "Bloque/Aptitud")
            self.grafo.add_edge("a1", bloque, label="evaluado", puntaje=puntaje)
        self.grafo.add_edge("b3", "c1", label="perfil de referencia")
        self.grafo.add_edge("b3", "c2", label="perfil de referencia")
        self.grafo.add_edge("b4", "c1", label="perfil de referencia")
        resultados = inferir_afinidades(self.grafo)
        self.assertEqual([(r.carrera_id, len(r.evidencias)) for r in resultados],
                         [("c1", 2), ("c2", 1)])


if __name__ == "__main__":
    unittest.main()
