import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import OWL, RDF

from inferencia import VOC
from poblar_ontologia import (CSV_PREDETERMINADO, cargar_csv_como_rdf,
                             imprimir_inferencia_perfil, inferir_perfil)


class PoblacionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rdf, cls.origenes = cargar_csv_como_rdf()

    def test_perfiles_y_evaluaciones_con_procedencia(self):
        self.assertEqual(self.origenes, {"real": 350, "synthetic": 1050})
        self.assertEqual(len(set(self.rdf.subjects(RDF.type, VOC.PerfilVocacional))), 1400)
        self.assertEqual(len(set(self.rdf.subjects(RDF.type, VOC.Evaluacion))), 12600)
        self.assertEqual(len(set(self.rdf.subjects(RDF.type, VOC.BloqueAptitud))), 9)
        self.assertEqual(len(set(self.rdf.subjects(RDF.type, VOC.Carrera))), 4)
        self.assertEqual(len(set(self.rdf.subjects(RDF.type, VOC.Alumno))), 0)
        self.assertIn((VOC.ontologia, RDF.type, OWL.Ontology), self.rdf)
        self.assertIsNotNone(self.rdf.value(VOC["perfil/00003"], VOC.valorAMAINormalizado))
        self.assertNotIn((VOC["perfil/00003"], VOC.interesPrincipal, VOC.b10), self.rdf)
        self.assertIsNotNone(self.rdf.value(VOC.ontologia, VOC.versionCriterio))

    def test_owl_se_puede_reabrir_e_inferir_sobre_un_perfil(self):
        with tempfile.TemporaryDirectory() as temp:
            salida = Path(temp) / "perfiles.owl"
            self.rdf.serialize(destination=str(salida), format="xml")
            cargado = Graph().parse(salida, format="xml")
            self.assertEqual(len(cargado), len(self.rdf))
            carreras = [nombre for nombre, _ in inferir_perfil(cargado, 2)]
            self.assertEqual(carreras, [
                "Ingenieria en Computacion (ICO)",
                "Ingenieria en Sistemas Inteligentes (ISC)",
            ])

    def test_rechaza_csv_modificado_sin_actualizar_procedencia(self):
        with CSV_PREDETERMINADO.open(encoding="utf-8-sig", newline="") as entrada:
            lector = csv.DictReader(entrada)
            filas = list(lector)
            columnas = lector.fieldnames
        filas[0]["calculo"] = "0.999999"
        with tempfile.TemporaryDirectory() as temp:
            csv_alterado = Path(temp) / "alterado.csv"
            with csv_alterado.open("w", encoding="utf-8", newline="") as salida:
                escritor = csv.DictWriter(salida, fieldnames=columnas)
                escritor.writeheader()
                escritor.writerows(filas)
            with self.assertRaisesRegex(ValueError, "Fila 1: la procedencia no coincide"):
                cargar_csv_como_rdf(csv_alterado)

    def test_perfil_7_muestra_convergencia_y_evidencia(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            imprimir_inferencia_perfil(self.rdf, 7)
        texto = salida.getvalue()
        self.assertIn("Ingenieria en Computacion (ICO) (convergencia de intereses)", texto)
        self.assertIn("Ingenieria en Sistemas Inteligentes (ISC) (convergencia de intereses)", texto)
        self.assertIn("Calculo=0.800279", texto)
        self.assertIn("Mecanico=0.793147", texto)

    def test_etiqueta_generada_no_participa_en_inferencia(self):
        perfil = VOC["perfil/00007"]
        original = self.rdf.value(perfil, VOC.etiquetaDelDataset)
        antes = inferir_perfil(self.rdf, 7)
        try:
            self.rdf.remove((perfil, VOC.etiquetaDelDataset, original))
            self.rdf.add((perfil, VOC.etiquetaDelDataset, VOC.c4))
            self.assertEqual(inferir_perfil(self.rdf, 7), antes)
        finally:
            self.rdf.remove((perfil, VOC.etiquetaDelDataset, VOC.c4))
            self.rdf.add((perfil, VOC.etiquetaDelDataset, original))

    def test_sin_interes_principal_se_abstiene(self):
        perfil = VOC["perfil/00007"]
        intereses = list(self.rdf.triples((perfil, VOC.interesPrincipal, None)))
        try:
            for triple in intereses:
                self.rdf.remove(triple)
            self.assertEqual(inferir_perfil(self.rdf, 7), [])
        finally:
            for triple in intereses:
                self.rdf.add(triple)


if __name__ == "__main__":
    unittest.main()
