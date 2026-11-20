"""Importa perfiles Hereford/AMAI de CSV y exporta una ontología RDF/XML (.owl)."""

import argparse
import csv
import hashlib
from collections import Counter
from decimal import Decimal, InvalidOperation
from itertools import zip_longest
from pathlib import Path

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import Graph, Literal
from rdflib.namespace import OWL, RDF, RDFS, XSD

from catalogo import BLOQUES, CARRERAS
from inferencia import VOC, agregar_regla_afinidad


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PREDETERMINADO = DATA_DIR / "conjunto_de_datos_aumentado_75_sintetico_amai.csv"
PROCEDENCIA_PREDETERMINADA = Path(__file__).resolve().parent / "procedencia_perfiles.csv"
SALIDA_PREDETERMINADA = Path(__file__).resolve().parent.parent / "artifacts" / "perfiles_vocacionales.owl"
UMBRAL_NORMALIZADO_DEMO = Decimal("0.85")

# Las nueve columnas de interés corresponden a b1-b9. AMAI se conserva aparte.
COLUMNAS_APTITUD = (
    ("calculo", "b1"),
    ("C. FísICO", "b2"),
    ("C. BiológICO", "b3"),
    ("MecanICO", "b4"),
    ("Servicio social", "b5"),
    ("Literario", "b6"),
    ("Persuasivo", "b7"),
    ("ArtístICO", "b8"),
    ("Musical", "b9"),
)
COLUMNAS_FIRMA = tuple(columna for columna, _ in COLUMNAS_APTITUD) + (
    "valor_amai_normalizado", "CARRERA_ACTUAL")


def _decimal_en_rango(texto, columna, fila):
    try:
        valor = Decimal(texto)
    except (InvalidOperation, TypeError):
        raise ValueError(f"Fila {fila}: {columna} no es un número válido.") from None
    if not valor.is_finite() or not Decimal("0") <= valor <= Decimal("1"):
        raise ValueError(f"Fila {fila}: {columna} debe estar entre 0 y 1.")
    return valor


def _esquema(rdf):
    rdf.bind("voc", VOC)
    rdf.add((VOC.ontologia, RDF.type, OWL.Ontology))
    for clase in (VOC.PerfilVocacional, VOC.BloqueAptitud, VOC.Carrera, VOC.Evaluacion):
        rdf.add((clase, RDF.type, OWL.Class))
    for propiedad in (VOC.tieneEvaluacion, VOC.bloque, VOC.importantePara,
                      VOC.destacaEn, VOC.etiquetaDelDataset):
        rdf.add((propiedad, RDF.type, OWL.ObjectProperty))
    for propiedad in (VOC.nombre, VOC.codigo, VOC.puntajeNormalizado,
                      VOC.valorAMAINormalizado, VOC.origenRegistro,
                      VOC.filaCSV, VOC.filaFuente):
        rdf.add((propiedad, RDF.type, OWL.DatatypeProperty))
    rdf.add((VOC.PerfilVocacional, RDFS.comment, Literal(
        "Registro de intereses; puede ser original o sintético. No identifica a un alumno.")))
    rdf.add((VOC.etiquetaDelDataset, RDFS.comment, Literal(
        "Etiqueta generada por el proceso histórico de reetiquetado; no es una carrera declarada.")))
    agregar_regla_afinidad(rdf)

    for carrera_id, nombre, codigo in CARRERAS:
        carrera = VOC[carrera_id]
        rdf.add((carrera, RDF.type, VOC.Carrera))
        rdf.add((carrera, VOC.nombre, Literal(nombre)))
        rdf.add((carrera, VOC.codigo, Literal(codigo)))
    for bloque_id, nombre, carrera_id in BLOQUES[:9]:
        bloque = VOC[bloque_id]
        rdf.add((bloque, RDF.type, VOC.BloqueAptitud))
        rdf.add((bloque, VOC.nombre, Literal(nombre)))
        rdf.add((bloque, VOC.importantePara, VOC[carrera_id]))


def cargar_csv_como_rdf(csv_path=CSV_PREDETERMINADO,
                        procedencia_path=PROCEDENCIA_PREDETERMINADA):
    """Carga perfiles y verifica la firma y procedencia de cada fila."""
    rdf = Graph()
    _esquema(rdf)
    carreras_por_codigo = {codigo: carrera_id for carrera_id, _, codigo in CARRERAS}
    origenes = Counter()

    with open(csv_path, encoding="utf-8-sig", newline="") as datos_file, \
         open(procedencia_path, encoding="utf-8-sig", newline="") as procedencia_file:
        datos = csv.DictReader(datos_file)
        procedencia = csv.DictReader(procedencia_file)
        requeridas = set(COLUMNAS_FIRMA)
        if not requeridas.issubset(datos.fieldnames or []):
            raise ValueError(f"Faltan columnas del CSV: {sorted(requeridas - set(datos.fieldnames or []))}")
        if not {"fila_csv", "origen", "fila_fuente", "sha256"}.issubset(procedencia.fieldnames or []):
            raise ValueError("El archivo de procedencia no contiene las columnas necesarias.")

        for fila, (registro, control) in enumerate(zip_longest(datos, procedencia), start=1):
            if registro is None or control is None:
                raise ValueError("El CSV y su archivo de procedencia tienen distinto número de filas.")
            firma = hashlib.sha256("\x1f".join(
                registro[columna] for columna in COLUMNAS_FIRMA).encode("utf-8")).hexdigest()
            if control["fila_csv"] != str(fila) or control["sha256"] != firma:
                raise ValueError(f"Fila {fila}: la procedencia no coincide con el CSV.")
            codigo = registro["CARRERA_ACTUAL"].strip()
            if codigo not in carreras_por_codigo:
                raise ValueError(f"Fila {fila}: etiqueta de carrera inválida.")
            origen = control["origen"].strip()
            if origen not in {"real", "synthetic"}:
                raise ValueError(f"Fila {fila}: origen desconocido: {origen!r}.")

            perfil = VOC[f"perfil/{fila:05d}"]
            rdf.add((perfil, RDF.type, VOC.PerfilVocacional))
            rdf.add((perfil, VOC.filaCSV, Literal(fila, datatype=XSD.integer)))
            rdf.add((perfil, VOC.origenRegistro, Literal(origen)))
            rdf.add((perfil, VOC.etiquetaDelDataset, VOC[carreras_por_codigo[codigo]]))
            if control["fila_fuente"]:
                rdf.add((perfil, VOC.filaFuente, Literal(
                    int(control["fila_fuente"]), datatype=XSD.integer)))
            amai = _decimal_en_rango(registro["valor_amai_normalizado"],
                                     "valor_amai_normalizado", fila)
            rdf.add((perfil, VOC.valorAMAINormalizado, Literal(amai)))

            for columna, bloque_id in COLUMNAS_APTITUD:
                puntaje = _decimal_en_rango(registro[columna], columna, fila)
                evaluacion = VOC[f"evaluacion/{fila:05d}/{bloque_id}"]
                rdf.add((evaluacion, RDF.type, VOC.Evaluacion))
                rdf.add((perfil, VOC.tieneEvaluacion, evaluacion))
                rdf.add((evaluacion, VOC.bloque, VOC[bloque_id]))
                rdf.add((evaluacion, VOC.puntajeNormalizado, Literal(puntaje)))
                if puntaje >= UMBRAL_NORMALIZADO_DEMO:
                    rdf.add((perfil, VOC.destacaEn, VOC[bloque_id]))
            origenes[origen] += 1

    return rdf, dict(origenes)


def inferir_perfil(rdf, fila):
    """Razona sobre un solo perfil para evitar expandir las 1,400 filas."""
    perfil = VOC[f"perfil/{fila:05d}"]
    if (perfil, RDF.type, VOC.PerfilVocacional) not in rdf:
        raise ValueError(f"No existe el perfil de la fila {fila}.")

    reducido = Graph()
    agregar_regla_afinidad(reducido)
    for triple in rdf.triples((None, VOC.importantePara, None)):
        reducido.add(triple)
    for triple in rdf.triples((perfil, VOC.destacaEn, None)):
        reducido.add(triple)
    DeductiveClosure(OWLRL_Semantics).expand(reducido)

    puntajes = {}
    for evaluacion in rdf.objects(perfil, VOC.tieneEvaluacion):
        bloque = rdf.value(evaluacion, VOC.bloque)
        puntajes[bloque] = rdf.value(evaluacion, VOC.puntajeNormalizado)

    resultados = []
    for carrera in sorted(reducido.objects(perfil, VOC.afinidadCon), key=str):
        evidencias = sorted(
            ((str(rdf.value(bloque, VOC.nombre)), str(puntajes[bloque]))
             for bloque in rdf.objects(perfil, VOC.destacaEn)
             if (bloque, VOC.importantePara, carrera) in reducido),
            key=lambda item: item[0],
        )
        resultados.append((str(rdf.value(carrera, VOC.nombre)), evidencias))
    return resultados


def imprimir_inferencia_perfil(rdf, fila):
    """Presenta la procedencia y la evidencia de un perfil del CSV."""
    resultados = inferir_perfil(rdf, fila)
    perfil = VOC[f"perfil/{fila:05d}"]
    origen = rdf.value(perfil, VOC.origenRegistro)
    etiqueta = rdf.value(perfil, VOC.etiquetaDelDataset)
    codigo = rdf.value(etiqueta, VOC.codigo)
    print(f"Afinidades demostrativas del perfil {fila} "
          f"(origen: {origen}; etiqueta generada: {codigo}):")
    for carrera, evidencias in resultados:
        print(f"  {carrera}: " + ", ".join(f"{nombre}={puntaje}" for nombre, puntaje in evidencias))
    if not resultados:
        print("  Ninguna con el umbral 0.85.")


def main():
    parser = argparse.ArgumentParser(description="Convierte perfiles CSV a OWL/RDF XML.")
    parser.add_argument("--csv", type=Path, default=CSV_PREDETERMINADO)
    parser.add_argument("--procedencia", type=Path, default=PROCEDENCIA_PREDETERMINADA)
    parser.add_argument("--salida", type=Path, default=SALIDA_PREDETERMINADA)
    parser.add_argument("--perfil", type=int, help="Muestra inferencias para una fila CSV.")
    args = parser.parse_args()

    rdf, origenes = cargar_csv_como_rdf(args.csv, args.procedencia)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    rdf.serialize(destination=str(args.salida), format="xml")
    print(f"Exportados {sum(origenes.values())} perfiles a {args.salida} "
          f"({origenes.get('real', 0)} originales; "
          f"{origenes.get('synthetic', 0)} sintéticos).")

    if args.perfil is not None:
        cargado = Graph().parse(args.salida, format="xml")
        imprimir_inferencia_perfil(cargado, args.perfil)


if __name__ == "__main__":
    main()
