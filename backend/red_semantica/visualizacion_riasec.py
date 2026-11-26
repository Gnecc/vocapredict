"""Vista del catálogo RDF que utiliza la inferencia RIASEC."""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from rdflib.namespace import RDF, RDFS

from riasec_owl import AREAS, VOC, cargar_catalogo, crear_grafo


def mostrar_predicados(red, posiciones, relaciones):
    aristas = [(origen, destino, etiqueta, color)
               for enlaces, etiqueta, color in relaciones for origen, destino in enlaces]
    if not aristas:
        return

    inicios = [posiciones[origen] for origen, _, _, _ in aristas]
    finales = [posiciones[destino] for _, destino, _, _ in aristas]
    aviso = red.annotate("", xy=(0, 0), xytext=(0, 13), textcoords="offset points",
                         ha="center", fontsize=9, zorder=10, annotation_clip=False,
                         bbox={"boxstyle": "round,pad=0.35", "fc": "white"})
    aviso.set_visible(False)

    def al_mover(evento):
        elegida = None
        if evento.inaxes is red:
            inicio = red.transData.transform(inicios)
            direccion = red.transData.transform(finales) - inicio
            relativo = np.array([evento.x, evento.y]) - inicio
            fraccion = np.einsum("ij,ij->i", relativo, direccion) / (direccion ** 2).sum(axis=1)
            distancia = np.linalg.norm(relativo - np.clip(fraccion, 0, 1)[:, None] * direccion, axis=1)
            # Cerca de los nodos se prioriza la etiqueta del nodo.
            distancia[(fraccion < 0.2) | (fraccion > 0.8)] = np.inf
            indice = distancia.argmin()
            if distancia[indice] <= 7:
                elegida = aristas[indice]

        if elegida is None:
            if not aviso.get_visible():
                return
            aviso.set_visible(False)
        else:
            _, _, etiqueta, color = elegida
            aviso.xy = (evento.xdata, evento.ydata)
            aviso.set_text(etiqueta)
            aviso.get_bbox_patch().set_edgecolor(color)
            aviso.set_visible(True)
        red.figure.canvas.draw_idle()

    red.figure.canvas.mpl_connect("motion_notify_event", al_mover)


def dibujar_catalogo_riasec(rdf):
    areas = [VOC[f"area/{letra}"] for letra in AREAS]
    carreras = sorted(rdf.subjects(RDF.type, VOC.OpcionVocacional),
                      key=lambda nodo: str(rdf.value(nodo, RDFS.label)).casefold())
    referencias = dict(rdf.subject_objects(VOC.tienePerfilReferencia))
    referencias.update(rdf.subject_objects(VOC.perfilExperimental))
    activas = [carrera for carrera in carreras if carrera in referencias]
    pendientes = [carrera for carrera in carreras if carrera not in referencias]

    grafo = nx.DiGraph()
    grafo.add_nodes_from([*areas, *activas, *(referencias[carrera] for carrera in activas)])
    respaldos = sorted(rdf.subject_objects(VOC.respaldaOpcion))
    perfiles = [(carrera, referencias[carrera]) for carrera in activas]
    grafo.add_edges_from(respaldos + perfiles)

    posiciones = {area: (0.15, 1 - (i + 0.5) / len(areas)) for i, area in enumerate(areas)}
    for i, carrera in enumerate(activas):
        altura = 1 - (i + 0.5) / len(activas)
        posiciones[carrera] = (0.60, altura)
        posiciones[referencias[carrera]] = (0.91, altura)

    if pendientes:
        figura, (red, catalogo) = plt.subplots(
            1, 2, figsize=(17, 9), gridspec_kw={"width_ratios": (2.15, 1)}, layout="constrained",
        )
    else:
        figura, red = plt.subplots(figsize=(15, 16), layout="constrained")
    figura.suptitle(
        f"Ontología RIASEC · {len(carreras)} opciones en el catálogo",
        fontsize=20, fontweight="bold",
    )
    red.set_title("Pasa el cursor sobre una flecha para ver la relación", fontsize=12, pad=12)
    relaciones = (
        (respaldos, "respalda opción", "#49705a"),
        (perfiles, "tiene perfil de referencia", "#4d6b89"),
    )
    for aristas, etiqueta, color in relaciones:
        nx.draw_networkx_edges(grafo, posiciones, edgelist=aristas, edge_color=color,
                               alpha=0.48, arrowsize=12, node_size=220, ax=red)
        if aristas:
            origen, destino = aristas[0]
            x1, y1 = posiciones[origen]
            x2, y2 = posiciones[destino]
            red.text((x1 + x2) / 2, (y1 + y2) / 2, etiqueta, color=color,
                     ha="center", va="center", fontsize=9, zorder=3,
                     bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none"})

    for nodo, (x, y) in posiciones.items():
        if nodo in areas:
            letra = str(nodo).rsplit("/", 1)[-1]
            etiqueta = f"{letra} · {rdf.value(nodo, RDFS.label)}"
            fondo = "#e1eee3"
        elif nodo in activas:
            etiqueta, fondo = str(rdf.value(nodo, RDFS.label)), "#ffffff"
        else:
            origen = str(rdf.value(nodo, VOC.estado))
            codigo = rdf.value(nodo, VOC.codigoRIASEC)
            etiqueta, fondo = {
                "experimental": (f"{codigo} · experimental", "#faebcc"),
                "derivado del CSV": (f"{codigo} · CSV", "#e1eee3"),
            }.get(origen, (f"{codigo} · Zenodo", "#e4eef6"))
        red.text(x, y, etiqueta, ha="center", va="center", fontsize=9,
                 bbox={"boxstyle": "round,pad=0.38", "fc": fondo, "ec": "#a7b9af"})
    red.set(xlim=(-0.01, 1.02), ylim=(0, 1))
    red.axis("off")
    mostrar_predicados(red, posiciones, relaciones)

    if pendientes:
        catalogo.set_title(f"Sin referencia activa · {len(pendientes)} opciones", fontsize=13, pad=18)
        for i, carrera in enumerate(pendientes):
            catalogo.text(0.04, 0.98 - (i + 0.5) / len(pendientes) * 0.91,
                          f"•  {rdf.value(carrera, RDFS.label)}", fontsize=9, va="center")
        catalogo.axis("off")
    return figura


def visualizar_catalogo_riasec():
    dibujar_catalogo_riasec(crear_grafo(cargar_catalogo(ampliar=True), "AEI"))
    plt.show()
