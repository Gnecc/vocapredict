"""Conexiones exploratorias OWL-RL a partir del grafo de demostración."""

from dataclasses import dataclass

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF

from criterio import AgenteIntereses, AgenteRevision


VOC = Namespace("urn:vocapredict:")
BLOQUE_SOCIOECONOMICO = "Situacion socioeconomica"
UMBRAL_DEMO = 70


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
    """Convierte intereses y vínculos de referencia a hechos RDF."""
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

    puntajes_por_alumno = {}
    for origen, destino, datos in grafo.edges(data=True):
        etiqueta = datos.get("label")
        if etiqueta not in {"perfil de referencia", "carrera sugerida", "evaluado"}:
            continue
        sujeto, objeto = VOC[str(origen)], VOC[str(destino)]
        if etiqueta == "perfil de referencia":
            rdf.add((sujeto, VOC.areaPerfilReferencia, objeto))
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
                if isinstance(puntaje, (int, float)) and destino != "b10" and \
                        grafo.nodes[destino].get("nombre") != BLOQUE_SOCIOECONOMICO:
                    puntajes_por_alumno.setdefault(origen, {})[destino] = puntaje / 100

    selector = AgenteIntereses()
    for alumno, puntajes in puntajes_por_alumno.items():
        for bloque in selector.seleccionar(puntajes, minimo=umbral / 100):
            rdf.add((VOC[str(alumno)], VOC.interesPrincipal, VOC[str(bloque)]))

    agregar_regla_afinidad(rdf)
    return rdf


def agregar_regla_afinidad(rdf):
    """Declara la regla OWL compartida por los ejemplos y perfiles importados."""
    cadena = BNode()
    Collection(rdf, cadena, [VOC.interesPrincipal, VOC.areaPerfilReferencia])
    rdf.add((VOC.conexionExploratoria, RDF.type, OWL.ObjectProperty))
    rdf.add((VOC.conexionExploratoria, OWL.propertyChainAxiom, cadena))


def inferir_afinidades(grafo, umbral=UMBRAL_DEMO):
    """Devuelve afinidades deducidas por OWL-RL, con su evidencia original."""
    rdf = construir_rdf(grafo, umbral)
    DeductiveClosure(OWLRL_Semantics).expand(rdf)
    resultados = []

    for alumno in sorted(rdf.subjects(RDF.type, VOC.Alumno), key=str):
        for carrera in sorted(rdf.objects(alumno, VOC.conexionExploratoria), key=str):
            evidencias = []
            for bloque in rdf.objects(alumno, VOC.interesPrincipal):
                if (bloque, VOC.areaPerfilReferencia, carrera) not in rdf:
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
    return sorted(resultados, key=lambda resultado: (
        resultado.alumno_id, -len(resultado.evidencias), resultado.carrera_id))


def imprimir_afinidades(grafo, umbral=UMBRAL_DEMO):
    """Muestra las relaciones inferidas y el camino que justifica cada una."""
    print(f"\nConexiones exploratorias (interés mínimo: {umbral}/100; dos áreas principales)")
    resultados = inferir_afinidades(grafo, umbral)
    if not resultados:
        print("No hay conexión sustentada por los intereses principales.")
    for resultado in resultados:
        alumno = grafo.nodes[resultado.alumno_id]
        carrera = grafo.nodes[resultado.carrera_id]
        nombre = f"{alumno.get('nombre', '')} {alumno.get('apellidos', '')}".strip()
        nivel = AgenteRevision().nivel(len(resultado.evidencias))
        print(f"\n{nombre} (NC: {alumno.get('no_control', resultado.alumno_id)}) -> {carrera['nombre']} ({nivel})")
        for evidencia in resultado.evidencias:
            print(f"  {evidencia.bloque}={evidencia.puntaje}/100; aparece en el perfil de referencia.")
    print("\nSon relaciones para explorar, no recomendaciones validadas.")


if __name__ == "__main__":
    from red_semantica import configurar_ontologia

    grafo, *_ = configurar_ontologia()
    imprimir_afinidades(grafo)
