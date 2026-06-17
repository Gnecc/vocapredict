import matplotlib.pyplot as plt
import networkx as nx
from clases import Alumno, Bloque, Carrera

G = nx.DiGraph()


clases = ["Persona", "Alumno", "Bloque", "Carrera"]

for c in clases:
    G.add_node(c, tipo="clase")

atributos = {
    "Persona": ["nombre"],
    "Alumno": ["no_control", "carrera_sugerida"],
    "Bloque": ["nombre", "puntaje"],
    "Carrera": ["nombre"]
}

for c, attrs in atributos.items():
    for attr in attrs:
        nodo = f"{c}_{attr}"
        G.add_node(nodo, tipo="atributo")
        G.add_edge(c, nodo, relacion="tiene")


G.add_edge("Alumno", "Persona", relacion="es_un")
G.add_edge("Alumno", "Bloque", relacion="tiene")
G.add_edge("Bloque", "Carrera", relacion="importancia_para")


# Crear objetos reales
a1 = Alumno("Juan", "2023001", "Sistemas")
b1 = Bloque("Matematico", 85)
c1 = Carrera("Ingenieria Sistemas")

# Nombres de nodos
G.add_node("a1", tipo="instancia")
G.add_node("b1", tipo="instancia")
G.add_node("c1", tipo="instancia")

# Relación instancia → clase
G.add_edge("a1", "Alumno", relacion="instancia_de")
G.add_edge("b1", "Bloque", relacion="instancia_de")
G.add_edge("c1", "Carrera", relacion="instancia_de")

# Relaciones entre instancias
G.add_edge("a1", "b1", relacion="tiene")
G.add_edge("b1", "c1", relacion="importancia_para")

G.add_node("a1_nombre:Juan", tipo="atributo")
G.add_node("a1_no_control:2023001", tipo="atributo")

G.add_edge("a1", "a1_nombre:Juan", relacion="tiene")
G.add_edge("a1", "a1_no_control:2023001", relacion="tiene")

G.add_node("b1_nombre:Matematico", tipo="atributo")
G.add_node("b1_puntaje:85", tipo="atributo")

G.add_edge("b1", "b1_nombre:Matematico", relacion="tiene")
G.add_edge("b1", "b1_puntaje:85", relacion="tiene")

G.add_node("c1_nombre:Ing.Sistemas", tipo="atributo")
G.add_edge("c1", "c1_nombre:Ing.Sistemas", relacion="tiene")


pos = {}

# Clases arriba
pos["Persona"] = (0, 3)
pos["Alumno"] = (2, 3)
pos["Bloque"] = (4, 3)
pos["Carrera"] = (6, 3)

# Instancias en medio
pos["a1"] = (2, 2)
pos["b1"] = (4, 2)
pos["c1"] = (6, 2)

# Atributos abajo
y_attr = 1
for nodo in G.nodes():
    if "nombre" in nodo or "puntaje" in nodo or "control" in nodo:
        pos[nodo] = (hash(nodo) % 7, y_attr)

colores = []
tamaños = []

for nodo, data in G.nodes(data=True):
    if data["tipo"] == "clase":
        colores.append("yellow")
        tamaños.append(2000)
    elif data["tipo"] == "instancia":
        colores.append("blue")
        tamaños.append(1200)
    else:
        colores.append("green")
        tamaños.append(600)

# Aristas
edge_colors = []
for u, v, data in G.edges(data=True):
    if G.nodes[u]["tipo"] == "instancia":
        edge_colors.append("purple")
    else:
        edge_colors.append("black")


plt.figure(figsize=(10,8))

nx.draw(G, pos,
        with_labels=True,
        node_color=colores,
        node_size=tamaños,
        edge_color=edge_colors,
        font_size=8)

# etiquetas de relaciones
labels = nx.get_edge_attributes(G, "relacion")
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=7)

plt.show()