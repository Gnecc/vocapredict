"""Catálogo RDF e inferencia exploratoria para seis puntajes RIASEC."""

import argparse
import csv
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
REFERENCIAS_CSV = Path(__file__).with_name("referencias_riasec_csv.json")
CSV_RIASEC = Path(__file__).resolve().parents[1] / "data" / "vocapredict_unificado_riasec.csv"
CPE_EXPERIMENTOS = ("AES", "AEI", "AIS", "IES")


def cargar_catalogo(*, ampliar=False):
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    if ampliar:
        referencias = json.loads(REFERENCIAS_CSV.read_text(encoding="utf-8"))
        for opcion in catalogo["opciones"]:
            if opcion["id"] in referencias:
                opcion["referencia"] = referencias[opcion["id"]]
    return catalogo


def crear_grafo(catalogo, cpe_experimental=None):
    if cpe_experimental is not None and cpe_experimental not in CPE_EXPERIMENTOS:
        raise ValueError("Código experimental desconocido para Comunicación y Periodismo.")
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
            agregar_referencia(grafo, perfil, referencia,
                               URIRef(referencia["fuente"]) if "fuente" in referencia else fuente,
                               "derivado del CSV" if "perfiles_entrenamiento" in referencia else "provisional")
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
    if cpe_experimental:
        nodo = VOC[f"opcion/{revision['opcion']}"]
        experimento = VOC[f"referencia/experimento-CPE-{cpe_experimental}"]
        fuente_experimento = fuente if cpe_experimental == "AES" else URIRef(revision["plan"])
        agregar_referencia(grafo, experimento, {
            "programa": revision["programa"], "codigo": cpe_experimental,
        }, fuente_experimento, "experimental")
        if cpe_experimental != "AES":
            grafo.add((experimento, RDFS.comment, Literal(
                "Variante experimental propuesta por VocaPredict a partir del plan de estudios.",
                lang="es",
            )))
        grafo.add((experimento, DCTERMS.isVersionOf, perfil))
        grafo.add((nodo, VOC.perfilExperimental, experimento))
        for letra in cpe_experimental:
            grafo.add((VOC[f"area/{letra}"], VOC.respaldaOpcion, nodo))
    return grafo


def agregar_referencia(grafo, perfil, referencia, fuente, estado):
    grafo.add((perfil, RDF.type, VOC.PerfilReferencia))
    grafo.add((perfil, RDFS.label, Literal(referencia["programa"], lang="es")))
    grafo.add((perfil, VOC.codigoRIASEC, Literal(referencia["codigo"])))
    grafo.add((perfil, VOC.estado, Literal(estado)))
    grafo.add((perfil, DCTERMS.source, fuente))
    if "perfiles_entrenamiento" in referencia:
        grafo.add((perfil, VOC.perfilesEntrenamiento, Literal(referencia["perfiles_entrenamiento"])))


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


def intereses_destacados(puntajes):
    """Excluye empates con el cuarto lugar de las seis áreas."""
    corte = sorted(puntajes.values(), reverse=True)[3]
    return {letra for letra, puntaje in puntajes.items() if puntaje > corte}


def inferir(catalogo, valores, cpe_experimental=None):
    puntajes = validar_puntajes(valores)
    destacados = intereses_destacados(puntajes)
    grafo = crear_grafo(catalogo, cpe_experimental)
    estudiante = VOC["estudiante/consulta"]
    grafo.add((estudiante, RDF.type, VOC.PerfilEstudiante))
    for letra, puntaje in puntajes.items():
        area = VOC[f"area/{letra}"]
        evaluacion = VOC[f"evaluacion/consulta/{letra}"]
        grafo.add((evaluacion, RDF.type, VOC.Evaluacion))
        grafo.add((estudiante, VOC.tieneEvaluacion, evaluacion))
        grafo.add((evaluacion, VOC.area, area))
        grafo.add((evaluacion, VOC.puntaje, Literal(puntaje)))
        if letra in destacados:
            grafo.add((estudiante, VOC.interesDestacado, area))
    DeductiveClosure(OWLRL_Semantics).expand(grafo)

    resultados = []
    for opcion in catalogo["opciones"]:
        nodo = VOC[f"opcion/{opcion['id']}"]
        if (estudiante, VOC.opcionCandidata, nodo) not in grafo:
            continue
        if opcion["id"] == catalogo["revision_fes_aragon"]["opcion"]:
            fuente = (catalogo["fuente_referencias"] if cpe_experimental == "AES"
                      else catalogo["revision_fes_aragon"]["plan"])
            opcion = {**opcion, "referencia": {"codigo": cpe_experimental},
                      "experimental": True, "fuente": fuente}
        codigo = opcion["referencia"]["codigo"]
        evidencia = [(letra, puntajes[letra]) for letra in codigo if letra in destacados]
        if len(evidencia) >= 2:
            grafo.add((estudiante, VOC.conexionExploratoria, nodo))
            resultados.append((opcion, evidencia))
    resultados.sort(key=lambda item: (-len(item[1]), item[0]["nombre"]))
    return grafo, resultados


def inferir_perfil_csv(catalogo, perfil, ruta=CSV_RIASEC, cpe_experimental=None):
    perfil = str(perfil).strip()
    if not perfil.isascii() or not perfil.isdecimal() or int(perfil) < 1:
        raise ValueError("Ingresa un identificador de origen RIASEC positivo.")
    perfil = str(int(perfil))
    columnas = [f"riasec_{area}" for area in AREAS]
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = csv.DictReader(archivo)
        requeridas = {"source_row_id", "source", "instrument", "riasec_eligible", *columnas}
        if not requeridas.issubset(filas.fieldnames or ()):
            raise ValueError("El CSV no contiene las columnas requeridas para RIASEC.")
        for fila in filas:
            if (fila["source"] != "openpsychometrics_riasec" or fila["instrument"] != "RIASEC"
                    or fila["source_row_id"] != perfil):
                continue
            if fila["riasec_eligible"] != "1":
                raise ValueError(f"El perfil RIASEC {perfil} no es elegible.")
            grafo, resultados = inferir(catalogo, [fila[columna] for columna in columnas], cpe_experimental)
            grafo.add((VOC["estudiante/consulta"], VOC.identificadorOrigen, Literal(int(perfil))))
            grafo.add((VOC["estudiante/consulta"], DCTERMS.source, Literal(f"OpenPsychometrics RIASEC, fila {perfil}")))
            return grafo, resultados
    raise ValueError(f"No existe el perfil de origen RIASEC {perfil}.")


def imprimir_inferencia(resultados, fuente):
    print("Conexiones exploratorias RIASEC")
    if not resultados:
        print("  Evidencia insuficiente para establecer una conexión.")
    for opcion, evidencia in resultados:
        estado = " · experimental" if opcion.get("experimental") else ""
        print(f"  {opcion['nombre']} ({opcion['referencia']['codigo']}{estado})")
        print("    " + ", ".join(f"{NOMBRES[letra]} {puntaje}" for letra, puntaje in evidencia))
        if opcion.get("experimental"):
            print("    Referencia del experimento: " + opcion["fuente"])
        elif "perfiles_entrenamiento" in opcion["referencia"]:
            print(f"    Referencia del CSV · {opcion['referencia']['perfiles_entrenamiento']} perfiles de entrenamiento")
    if resultados:
        print("  Fuente de las referencias de Zenodo: " + fuente)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    consulta = parser.add_mutually_exclusive_group()
    consulta.add_argument("--perfil-riasec", metavar="ID", help="Identificador source_row_id en el CSV unificado.")
    consulta.add_argument("--puntajes", nargs=6, metavar="VALOR", help="En orden R I A S E C.")
    parser.add_argument("--catalogo", action="store_true", help="Lista las opciones y sus perfiles.")
    parser.add_argument("--catalogo-ampliado", action="store_true",
                        help="Usa las referencias derivadas del CSV y el perfil experimental AEI.")
    parser.add_argument("--cpe-experimental", choices=CPE_EXPERIMENTOS,
                        help="Prueba un código de Comunicación y Periodismo.")
    parser.add_argument("--salida", type=Path, help="Exporta el grafo a OWL en formato RDF/XML.")
    args = parser.parse_args()
    catalogo = cargar_catalogo(ampliar=args.catalogo_ampliado)
    if args.catalogo_ampliado and args.cpe_experimental is None:
        args.cpe_experimental = "AEI"
    if args.catalogo:
        for opcion in catalogo["opciones"]:
            if opcion["id"] == "CPE":
                codigo = f"{args.cpe_experimental} · experimental" if args.cpe_experimental else "en revisión"
            else:
                codigo = opcion.get("referencia", {}).get("codigo", "pendiente")
            print(f"{opcion['id']} · {opcion['nombre']} · {codigo}")
    if args.puntajes or args.perfil_riasec is not None:
        try:
            if args.perfil_riasec is not None:
                grafo, resultados = inferir_perfil_csv(catalogo, args.perfil_riasec, cpe_experimental=args.cpe_experimental)
            else:
                grafo, resultados = inferir(catalogo, args.puntajes, args.cpe_experimental)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        imprimir_inferencia(resultados, catalogo["fuente_referencias"])
    elif args.salida:
        grafo = crear_grafo(catalogo, args.cpe_experimental)
    elif not args.catalogo:
        parser.print_help()
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        grafo.serialize(destination=str(args.salida), format="xml")


if __name__ == "__main__":
    main()
