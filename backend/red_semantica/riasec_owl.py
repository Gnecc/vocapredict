"""Catálogo RDF e inferencia exploratoria para seis puntajes RIASEC."""

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS


VOC = Namespace("urn:vocapredict:riasec:")
AREAS = "RIASEC"
NOMBRES = dict(zip(AREAS, (
    "Realista", "Investigador", "Artístico", "Social", "Emprendedor", "Convencional",
)))
CATALOGO = Path(__file__).with_name("catalogo_riasec.json")


def cargar_catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def crear_grafo(catalogo):
    grafo = Graph()
    grafo.bind("voc", VOC)
    grafo.add((VOC.ontologia, RDF.type, OWL.Ontology))
    for clase in (VOC.OpcionVocacional, VOC.PerfilReferencia, VOC.AreaInteres,
                  VOC.PerfilEstudiante, VOC.Evaluacion, VOC.ProgramaOfertado):
        grafo.add((clase, RDF.type, OWL.Class))
    for letra, nombre in NOMBRES.items():
        area = VOC[f"area/{letra}"]
        grafo.add((area, RDF.type, VOC.AreaInteres))
        grafo.add((area, RDFS.label, Literal(nombre, lang="es")))

    cadena = BNode()
    Collection(grafo, cadena, [VOC.interesDestacado, VOC.respaldaOpcion])
    grafo.add((VOC.opcionCandidata, RDF.type, OWL.ObjectProperty))
    grafo.add((VOC.opcionCandidata, OWL.propertyChainAxiom, cadena))

    fuente = URIRef(catalogo["fuente_referencias"])
    for opcion in catalogo["opciones"]:
        nodo = VOC[f"opcion/{opcion['id']}"]
        grafo.add((nodo, RDF.type, VOC.OpcionVocacional))
        grafo.add((nodo, RDFS.label, Literal(opcion["nombre"], lang="es")))
        referencia = opcion.get("referencia")
        if referencia:
            perfil = VOC[f"referencia/{opcion['id']}"]
            agregar_referencia(grafo, perfil, referencia, fuente, "provisional")
            grafo.add((nodo, VOC.tienePerfilReferencia, perfil))
            for letra in referencia["codigo"]:
                grafo.add((VOC[f"area/{letra}"], VOC.respaldaOpcion, nodo))

    revision = catalogo["revision_fes_aragon"]
    programa = VOC["programa/fes-aragon-comunicacion-periodismo"]
    perfil = VOC["referencia/CPE"]
    agregar_referencia(grafo, perfil, revision["referencia"], fuente, "revision_curricular")
    grafo.add((programa, RDF.type, VOC.ProgramaOfertado))
    grafo.add((programa, RDFS.label, Literal(revision["programa"], lang="es")))
    grafo.add((programa, VOC.institucion, Literal(revision["institucion"])))
    grafo.add((programa, VOC.municipio, Literal(revision["municipio"])))
    grafo.add((programa, DCTERMS.source, URIRef(revision["oferta"])))
    grafo.add((programa, VOC.planEstudios, URIRef(revision["plan"])))
    grafo.add((programa, VOC.correspondeAOpcion, VOC[f"opcion/{revision['opcion']}"]))
    grafo.add((programa, VOC.tienePerfilReferencia, perfil))
    grafo.add((perfil, RDFS.comment, Literal(revision["decision"], lang="es")))
    for letra, evidencia in revision["evidencia"].items():
        nota = VOC[f"revision/fes-aragon/{letra}"]
        grafo.add((perfil, VOC.evidenciaCurricular, nota))
        grafo.add((nota, VOC.area, VOC[f"area/{letra}"]))
        grafo.add((nota, RDFS.comment, Literal(evidencia, lang="es")))
        grafo.add((nota, DCTERMS.source, URIRef(revision["plan"])))
    return grafo


def agregar_referencia(grafo, perfil, referencia, fuente, estado):
    grafo.add((perfil, RDF.type, VOC.PerfilReferencia))
    grafo.add((perfil, RDFS.label, Literal(referencia["programa"], lang="es")))
    grafo.add((perfil, VOC.codigoRIASEC, Literal(referencia["codigo"])))
    grafo.add((perfil, VOC.estado, Literal(estado)))
    grafo.add((perfil, DCTERMS.source, fuente))


def validar_puntajes(valores):
    mensaje = "Se requieren seis puntajes de 0.2 a 1 en orden R I A S E C."
    try:
        puntajes = tuple(Decimal(str(valor)) for valor in valores)
    except InvalidOperation:
        raise ValueError(mensaje) from None
    if len(puntajes) != 6 or any(
        not valor.is_finite() or not Decimal("0.2") <= valor <= 1 for valor in puntajes
    ):
        raise ValueError(mensaje)
    return dict(zip(AREAS, puntajes))


def inferir(catalogo, valores):
    puntajes = validar_puntajes(valores)
    grafo = crear_grafo(catalogo)
    estudiante = VOC["estudiante/consulta"]
    grafo.add((estudiante, RDF.type, VOC.PerfilEstudiante))
    # Include only areas that clearly outrank the fourth place. A tie at
    # the boundary provides insufficient evidence to pick between areas.
    corte = sorted(puntajes.values(), reverse=True)[3]
    for letra, puntaje in puntajes.items():
        area = VOC[f"area/{letra}"]
        evaluacion = VOC[f"evaluacion/consulta/{letra}"]
        grafo.add((evaluacion, RDF.type, VOC.Evaluacion))
        grafo.add((estudiante, VOC.tieneEvaluacion, evaluacion))
        grafo.add((evaluacion, VOC.area, area))
        grafo.add((evaluacion, VOC.puntaje, Literal(puntaje)))
        if puntaje > corte:
            grafo.add((estudiante, VOC.interesDestacado, area))
    DeductiveClosure(OWLRL_Semantics).expand(grafo)

    resultados = []
    for opcion in catalogo["opciones"]:
        nodo = VOC[f"opcion/{opcion['id']}"]
        if (estudiante, VOC.opcionCandidata, nodo) not in grafo:
            continue
        codigo = opcion["referencia"]["codigo"]
        evidencia = [(letra, puntajes[letra]) for letra in codigo if puntajes[letra] > corte]
        if len(evidencia) >= 2:
            grafo.add((estudiante, VOC.conexionExploratoria, nodo))
            resultados.append((opcion, evidencia))
    resultados.sort(key=lambda item: (-len(item[1]), item[0]["nombre"]))
    return grafo, resultados


def imprimir_inferencia(resultados, fuente):
    print("Conexiones exploratorias RIASEC")
    if not resultados:
        print("  Evidencia insuficiente para establecer una conexión.")
    for opcion, evidencia in resultados:
        print(f"  {opcion['nombre']} ({opcion['referencia']['codigo']})")
        print("    " + ", ".join(f"{NOMBRES[letra]} {puntaje}" for letra, puntaje in evidencia))
    if resultados:
        print("  Fuente de los perfiles provisionales: " + fuente)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puntajes", nargs=6, metavar="VALOR", help="En orden R I A S E C.")
    parser.add_argument("--catalogo", action="store_true", help="Lista las opciones y sus perfiles.")
    parser.add_argument("--salida", type=Path, help="Exporta el grafo a OWL en formato RDF/XML.")
    args = parser.parse_args()
    catalogo = cargar_catalogo()
    if args.catalogo:
        for opcion in catalogo["opciones"]:
            codigo = opcion.get("referencia", {}).get("codigo", "en revisión" if opcion["id"] == "CPE" else "pendiente")
            print(f"{opcion['id']} · {opcion['nombre']} · {codigo}")
    if args.puntajes:
        try:
            grafo, resultados = inferir(catalogo, args.puntajes)
        except ValueError as error:
            parser.error(str(error))
        imprimir_inferencia(resultados, catalogo["fuente_referencias"])
    elif args.salida:
        grafo = crear_grafo(catalogo)
    elif not args.catalogo:
        parser.print_help()
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        grafo.serialize(destination=str(args.salida), format="xml")


if __name__ == "__main__":
    main()
