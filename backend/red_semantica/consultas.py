"""Consultas sobre el grafo: por enlace, por data property y por nodo."""
from utils import formato_relacion, nombre_nodo, props_de_arista


# --- CONSULTAS SOBRE EL GRAFO ---
def nombre_nodo(G, n):
    d = G.nodes[n]
    if "apellidos" in d:
        return f"{d.get('nombre')} {d.get('apellidos')}".strip()
    return d.get("nombre", n)


def props_de_arista(d):
    return {k: val for k, val in d.items() if k != "label"}


def consulta_por_enlace(G, etiqueta):
    """Tipo 1: lista todos los enlaces de un tipo de relación."""
    resultados = [(u, v, d) for u, v, d in G.edges(data=True)
                  if d.get("label", "").lower() == etiqueta.lower()]
    if not resultados:
        print(f"\n[!] No existen enlaces con la relación '{etiqueta}'.")
        return
    print(f"\n--- ENLACES '{etiqueta}' ({len(resultados)}) ---")
    for u, v, d in resultados:
        print(f"[{u}] {nombre_nodo(G, u)} -- {formato_relacion(d['label'], props_de_arista(d))} --> [{v}] {nombre_nodo(G, v)}")


def consulta_por_propiedad(G, minimo, maximo):
    """Tipo 2: filtra enlaces 'evaluado' por la data property puntaje."""
    resultados = [(u, v, d) for u, v, d in G.edges(data=True)
                  if "puntaje" in d and minimo <= d["puntaje"] <= maximo]
    resultados.sort(key=lambda x: x[2]["puntaje"], reverse=True)
    if not resultados:
        print(f"\n[!] No hay evaluaciones con puntaje entre {minimo} y {maximo}.")
        return
    print(f"\n--- EVALUACIONES CON PUNTAJE ENTRE {minimo} Y {maximo} ({len(resultados)}) ---")
    for u, v, d in resultados:
        print(f"[{u}] {nombre_nodo(G, u)} -- {formato_relacion(d['label'], props_de_arista(d))} --> [{v}] {nombre_nodo(G, v)}")


def consulta_por_nodo(G, nodo_id):
    """Tipo 3: a qué nodos lleva un nodo y qué nodos llegan a él."""
    if nodo_id not in G or G.nodes[nodo_id].get("tipo") != "instancia":
        print(f"\n[!] El nodo '{nodo_id}' no existe o no es una instancia.")
        return
    print(f"\n--- NODO [{nodo_id}] {nombre_nodo(G, nodo_id)} ---")

    print("  Lleva a:")
    for _, v, d in G.out_edges(nodo_id, data=True):
        if d.get("label"):
            print(f"    -- {formato_relacion(d['label'], props_de_arista(d))} --> [{v}] {nombre_nodo(G, v)}")

    print("  Llegan a él:")
    for u, _, d in G.in_edges(nodo_id, data=True):
        if d.get("label"):
            print(f"    [{u}] {nombre_nodo(G, u)} -- {formato_relacion(d['label'], props_de_arista(d))} -->")
