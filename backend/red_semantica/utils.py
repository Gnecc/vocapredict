"""Funciones auxiliares compartidas por varios módulos."""


def formato_relacion(etiqueta, props=None):
    """Devuelve 'evaluado : 63' (etiqueta + data properties de la relación, sin paréntesis)."""
    valores = ", ".join(str(v) for v in (props or {}).values())
    return f"{etiqueta} : {valores}" if valores else etiqueta


def nombre_nodo(G, n):
    d = G.nodes[n]
    if "apellidos" in d:
        return f"{d.get('nombre')} {d.get('apellidos')}".strip()
    return d.get("nombre", n)


def props_de_arista(d):
    return {k: val for k, val in d.items() if k != "label"}
