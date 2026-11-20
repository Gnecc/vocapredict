"""Inferencia demostrativa de afinidades a partir del grafo NetworkX existente."""

from dataclasses import dataclass

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF


VOC = Namespace("urn:vocapredict:")
BLOQUE_SOCIOECONOMICO = "Situacion socioeconomica"
UMBRAL_DEMO = 85


@dataclass(frozen=True)
class Evidencia:
    bloque: str
    puntaje: int


@dataclass(frozen=True)
class Afinidad:
    alumno_id: str
    carrera_id: str
    evidencias: tuple[Evidencia, ...]


def construir_rdf(grafo, umbral=UMBRAL_DEMO):
    """Convierte hechos a RDF y declara la cadena de propiedades OWL.

    El umbral solo genera `destacaEn`; OWL-RL deduce `afinidadCon` mediante
    `destacaEn` + `importantePara`. No usa `carrera sugerida`.
    """
    if not isinstance(umbral, int) or not 0 <= umbral <= 100:
        raise ValueError("El umbral debe ser un entero entre 0 y 100.")

    rdf = Graph()
    rdf.bind("voc", VOC)
    for nodo_id, datos in grafo.nodes(data=True):
        if datos.get("tipo") != "instancia":
            continue
        recurso = VOC[str(nodo_id)]
        for clase, tipo_rdf in (
            ("Alumno", VOC.Alumno),
            ("Bloque/Aptitud", VOC.BloqueAptitud),
            ("Carrera", VOC.Carrera),
        ):
            if grafo.has_edge(nodo_id, clase):
                rdf.add((recurso, RDF.type, tipo_rdf))
                break
        if "nombre" in datos:
            rdf.add((recurso, VOC.nombre, Literal(datos["nombre"])))

    for origen, destino, datos in grafo.edges(data=True):
        etiqueta = datos.get("label")
        if etiqueta not in {"importante para", "carrera sugerida", "evaluado"}:
            continue
        sujeto, objeto = VOC[str(origen)], VOC[str(destino)]
        if etiqueta == "importante para":
            rdf.add((sujeto, VOC.importantePara, objeto))
        elif etiqueta == "carrera sugerida":
            rdf.add((sujeto, VOC.carreraSugeridaPrevia, objeto))
        elif etiqueta == "evaluado":
            evaluacion = VOC[f"evaluacion/{origen}/{destino}"]
            rdf.add((evaluacion, RDF.type, VOC.Evaluacion))
            rdf.add((evaluacion, VOC.alumno, sujeto))
            rdf.add((evaluacion, VOC.bloque, objeto))
            puntaje = datos.get("puntaje")
            if puntaje is not None:
                rdf.add((evaluacion, VOC.puntaje, Literal(puntaje)))
                if (
                    isinstance(puntaje, (int, float))
                    and puntaje >= umbral
                    and grafo.nodes[destino].get("nombre") != BLOQUE_SOCIOECONOMICO
                ):
                    rdf.add((sujeto, VOC.destacaEn, objeto))

    cadena = BNode()
    Collection(rdf, cadena, [VOC.destacaEn, VOC.importantePara])
    rdf.add((VOC.afinidadCon, RDF.type, OWL.ObjectProperty))
    rdf.add((VOC.afinidadCon, OWL.propertyChainAxiom, cadena))
    return rdf


def inferir_afinidades(grafo, umbral=UMBRAL_DEMO):
    """Devuelve afinidades deducidas por OWL-RL, con su evidencia original."""
    rdf = construir_rdf(grafo, umbral)
    DeductiveClosure(OWLRL_Semantics).expand(rdf)
    resultados = []

    for alumno in sorted(rdf.subjects(RDF.type, VOC.Alumno), key=str):
        for carrera in sorted(rdf.objects(alumno, VOC.afinidadCon), key=str):
            evidencias = []
            for bloque in rdf.objects(alumno, VOC.destacaEn):
                if (bloque, VOC.importantePara, carrera) not in rdf:
                    continue
                bloque_id = str(bloque).removeprefix(str(VOC))
                alumno_id = str(alumno).removeprefix(str(VOC))
                evidencias.append(Evidencia(
                    bloque=grafo.nodes[bloque_id]["nombre"],
                    puntaje=grafo.edges[alumno_id, bloque_id]["puntaje"],
                ))
            resultados.append(Afinidad(
                alumno_id=str(alumno).removeprefix(str(VOC)),
                carrera_id=str(carrera).removeprefix(str(VOC)),
                evidencias=tuple(sorted(evidencias, key=lambda e: e.bloque)),
            ))
    return resultados


def imprimir_afinidades(grafo, umbral=UMBRAL_DEMO):
    """Muestra las relaciones inferidas y el camino que justifica cada una."""
    print(f"\nAfinidades de demostración (umbral de aptitud: {umbral})")
    resultados = inferir_afinidades(grafo, umbral)
    if not resultados:
        print("No se infirieron afinidades con este umbral.")
    for resultado in resultados:
        alumno = grafo.nodes[resultado.alumno_id]
        carrera = grafo.nodes[resultado.carrera_id]
        nombre = f"{alumno.get('nombre', '')} {alumno.get('apellidos', '')}".strip()
        print(f"\n{nombre} (NC: {alumno.get('no_control', resultado.alumno_id)}) -> {carrera['nombre']}")
        for evidencia in resultado.evidencias:
            print(f"  {nombre} destaca en {evidencia.bloque} ({evidencia.puntaje}); "
                  f"{evidencia.bloque} es importante para esta carrera.")
    print("\nSon relaciones para explorar, no recomendaciones validadas.")


if __name__ == "__main__":
    from red_semantica import configurar_ontologia

    grafo, *_ = configurar_ontologia()
    imprimir_afinidades(grafo)
