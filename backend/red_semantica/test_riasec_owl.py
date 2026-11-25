import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rdflib import Graph
from rdflib.namespace import DCTERMS, RDF

from riasec_owl import AREAS, VOC, cargar_catalogo, crear_grafo, inferir, inferir_perfil_csv


class OntologiaRiasecTest(unittest.TestCase):
    def setUp(self):
        self.catalogo = cargar_catalogo()
        self.estudiante = VOC["estudiante/consulta"]

    def test_consulta_csv_usa_origen_y_puntajes_riasec(self):
        with TemporaryDirectory() as directory:
            ruta = Path(directory) / "perfiles.csv"
            ruta.write_text(
                "source,source_row_id,instrument,riasec_eligible,riasec_R,riasec_I,riasec_A,riasec_S,riasec_E,riasec_C\n"
                "vocapredict_augmented,7,Hereford,0,,,,,,\n"
                "openpsychometrics_riasec,7,RIASEC,1,.6,.95,.3,.4,.5,.9\n"
                "openpsychometrics_riasec,8,RIASEC,0,,,,,,\n",
                encoding="utf-8",
            )
            grafo, resultados = inferir_perfil_csv(self.catalogo, "7", ruta)
            _, manual = inferir(self.catalogo, [".6", ".95", ".3", ".4", ".5", ".9"])
            self.assertEqual(resultados, manual)
            self.assertEqual(grafo.value(self.estudiante, VOC.identificadorOrigen).toPython(), 7)
            for perfil, error in (("8", "no es elegible"), ("9", "No existe"), ("0", "positivo")):
                with self.subTest(perfil=perfil), self.assertRaisesRegex(ValueError, error):
                    inferir_perfil_csv(self.catalogo, perfil, ruta)

    def test_catalogo_owl_y_revision_fes_aragon(self):
        grafo = crear_grafo(self.catalogo)
        copia = Graph().parse(data=grafo.serialize(format="xml"), format="xml")
        self.assertEqual(len(set(copia.subjects(RDF.type, VOC.OpcionVocacional))), 42)
        self.assertEqual(len(set(copia.subject_objects(VOC.respaldaOpcion))), 39)
        programa = VOC["programa/fes-aragon-comunicacion-periodismo"]
        self.assertIn((programa, VOC.correspondeAOpcion, VOC["opcion/CPE"]), copia)
        self.assertIsNotNone(copia.value(programa, VOC.planEstudios))
        self.assertIsNotNone(copia.value(VOC["referencia/CPE"], DCTERMS.source))

    def test_los_13_perfiles_se_pueden_inferir(self):
        referencias = [opcion for opcion in self.catalogo["opciones"] if "referencia" in opcion]
        self.assertEqual(len(referencias), 13)
        for opcion in referencias:
            codigo = opcion["referencia"]["codigo"]
            with self.subTest(opcion=opcion["id"]):
                valores = ["0.9" if letra in codigo else "0.4" for letra in AREAS]
                grafo, resultados = inferir(self.catalogo, valores)
                nodo = VOC[f"opcion/{opcion['id']}"]
                self.assertIn((self.estudiante, VOC.opcionCandidata, nodo), grafo)
                self.assertIn((self.estudiante, VOC.conexionExploratoria, nodo), grafo)
                evidencia = dict((o["id"], e) for o, e in resultados)[opcion["id"]]
                self.assertEqual("".join(letra for letra, _ in evidencia), codigo)
                self.assertFalse(any(o["id"] == "CPE" for o, _ in resultados))

    def test_una_coincidencia_y_empates_insuficientes(self):
        grafo, resultados = inferir(self.catalogo, [".8", ".8", ".8", ".8", ".8", ".9"])
        self.assertEqual(resultados, [])
        nodo = VOC["opcion/IND"]
        self.assertIn((self.estudiante, VOC.opcionCandidata, nodo), grafo)
        self.assertNotIn((self.estudiante, VOC.conexionExploratoria, nodo), grafo)
        self.assertEqual(inferir(self.catalogo, [".8"] * 6)[1], [])

    def test_cpe_experimental_cambia_evidencia_segun_el_codigo(self):
        valores = [".8", ".95", ".9", ".3", ".4", ".2"]
        opcion_cpe = VOC["opcion/CPE"]
        consulta = (self.estudiante, VOC.conexionExploratoria, opcion_cpe)
        self.assertNotIn(consulta, inferir(self.catalogo, valores)[0])
        self.assertNotIn(consulta, inferir(self.catalogo, valores, "AES")[0])
        grafo, resultados = inferir(self.catalogo, valores, "AEI")
        self.assertIn(consulta, grafo)
        evidencia = next(e for o, e in resultados if o["id"] == "CPE")
        self.assertEqual([letra for letra, _ in evidencia], ["A", "I"])
        perfil = grafo.value(opcion_cpe, VOC.perfilExperimental)
        self.assertEqual(str(grafo.value(perfil, VOC.estado)), "experimental")
        self.assertEqual(str(grafo.value(perfil, DCTERMS.source)),
                         self.catalogo["revision_fes_aragon"]["plan"])

    def test_rechaza_puntajes_invalidos(self):
        for valores in ([0.5] * 5, [1.01] * 6, ["NaN"] * 6, ["x"] * 6):
            with self.subTest(valores=valores), self.assertRaises(ValueError):
                inferir(self.catalogo, valores)
