import networkx as nx
import matplotlib.pyplot as plt
from clases import Alumno, BloqueAptitud, Carrera

G = nx.DiGraph()

clases = ["Thing", "Persona", "Alumno", "Bloque/Aptitud", "Carrera"]
G.add_nodes_from(clases, tipo="clase")

# Instancias
a1 = Alumno("a1", "Juan Perez", "202301", "ICO")
a2 = Alumno("a2", "Maria Lopez", "202302", "ISC")
a3 = Alumno("a3", "Carlos Ruiz", "202303", "LIA")

b1 = BloqueAptitud("b1", "Calculo", 0.85)
b2 = BloqueAptitud("b2", "C. Fisico", 0.78)
b3 = BloqueAptitud("b3", "C. Biologico", 0.90)
b4 = BloqueAptitud("b4", "Mecanico", 0.70)
b5 = BloqueAptitud("b5", "Servicio social", 0.88)
b6 = BloqueAptitud("b6", "Literario", 0.92)
b7 = BloqueAptitud("b7", "Persuasivo", 0.80)
b8 = BloqueAptitud("b8", "Artistico", 0.75)
b9 = BloqueAptitud("b9", "Musical", 0.60)
b10 = BloqueAptitud("b10", "Situacion socioeconomica", 0.95)

c1 = Carrera("c1", "Ingenieria en Computacion (ICO)")
c2 = Carrera("c2", "Licenciatura en Informatica Administrativa (LIA)")
c3 = Carrera("c3", "Ingenieria en Sistemas Inteligentes (ISC)")
c4 = Carrera("c4", "Licenciatura en Lenguas (LLE)")

alumnos = [a1, a2, a3]
bloques = [b1,b2,b3,b4,b5,b6,b7,b8,b9,b10]
carreras = [c1,c2,c3,c4]

for a in alumnos:
    G.add_node(a.get_id(), tipo="instancia")
    G.add_edge(a.get_id(), "Alumno")
    
    G.add_node(f"nombre_{a.get_id()}:{a.get_nombre()}", tipo="atributo")
    G.add_node(f"nc_{a.get_id()}:{a.get_no_control()}", tipo="atributo")
    G.add_node(f"cs_{a.get_id()}:{a.get_carrera_sugerida()}", tipo="atributo")
    
    G.add_edge(a.get_id(), f"nombre_{a.get_id()}:{a.get_nombre()}")
    G.add_edge(a.get_id(), f"nc_{a.get_id()}:{a.get_no_control()}")
    G.add_edge(a.get_id(), f"cs_{a.get_id()}:{a.get_carrera_sugerida()}")

for b in bloques:
    G.add_node(b.get_id(), tipo="instancia")
    G.add_edge(b.get_id(), "Bloque/Aptitud")
    
    G.add_node(f"nombre_{b.get_id()}:{b.get_nombre()}", tipo="atributo")
    G.add_node(f"puntaje_{b.get_id()}:{b.get_puntaje()}", tipo="atributo")
    
    G.add_edge(b.get_id(), f"nombre_{b.get_id()}:{b.get_nombre()}")
    G.add_edge(b.get_id(), f"puntaje_{b.get_id()}:{b.get_puntaje()}")

for c in carreras:
    G.add_node(c.get_id(), tipo="instancia")
    G.add_edge(c.get_id(), "Carrera")
    
    G.add_node(f"nombre_{c.get_id()}:{c.get_nombre()}", tipo="atributo")
    G.add_edge(c.get_id(), f"nombre_{c.get_id()}:{c.get_nombre()}")


relaciones_instancias = [
    # Alumno "tiene" Bloque/Aptitud
    (a1.get_id(), b1.get_id(), "tiene"),
    (a1.get_id(), b2.get_id(), "tiene"),
    (a2.get_id(), b3.get_id(), "tiene"),
    (a2.get_id(), b4.get_id(), "tiene"),
    (a3.get_id(), b5.get_id(), "tiene"),
    (a3.get_id(), b6.get_id(), "tiene"),
    (a1.get_id(), b7.get_id(), "tiene"),
    (a2.get_id(), b8.get_id(), "tiene"),
    (a3.get_id(), b9.get_id(), "tiene"),
    (a1.get_id(), b10.get_id(), "tiene"),
    
    # Bloque/Aptitud es "importante para" Carrera
    (b1.get_id(), c1.get_id(), "importante para"),
    (b2.get_id(), c1.get_id(), "importante para"),
    (b3.get_id(), c2.get_id(), "importante para"),
    (b4.get_id(), c3.get_id(), "importante para"),
    (b5.get_id(), c4.get_id(), "importante para"),
    (b6.get_id(), c4.get_id(), "importante para"),
    (b7.get_id(), c2.get_id(), "importante para"),
    (b8.get_id(), c4.get_id(), "importante para"),
    (b9.get_id(), c4.get_id(), "importante para"),
    (b10.get_id(), c1.get_id(), "importante para")
]

for origen, destino, etiqueta in relaciones_instancias:
    G.add_edge(origen, destino, label=etiqueta)

# Relaciones estáticas entre clases
G.add_edges_from([
    ("Persona", "Thing"),
    ("Carrera", "Thing"),
    ("Bloque/Aptitud", "Thing"),
    ("Alumno", "Persona")
])


pos = {}

pos["Thing"] = (5, 6)
pos["Persona"] = (2, 5)
pos["Bloque/Aptitud"] = (5, 5)
pos["Carrera"] = (8, 5)
pos["Alumno"] = (2, 4)

instancias = [n for n, d in G.nodes(data=True) if d["tipo"] == "instancia"]
inst_a = sorted([n for n in instancias if n.startswith("a")])
inst_b = sorted([n for n in instancias if n.startswith("b")], key=lambda x: int(x[1:]))
inst_c = sorted([n for n in instancias if n.startswith("c")])

def asignar_eje_x(nodos, start_x, end_x, y):
    if not nodos: return
    if len(nodos) == 1:
        pos[nodos[0]] = ((start_x + end_x) / 2, y)
        return
    step = (end_x - start_x) / (len(nodos) - 1)
    for i, nodo in enumerate(nodos):
        pos[nodo] = (start_x + i * step, y)

asignar_eje_x(inst_a, 0.5, 3.5, 3) # Alumnos a la izquierda
asignar_eje_x(inst_b, 4, 6, 3)     # Bloques en el centro
asignar_eje_x(inst_c, 6.5, 9.5, 3) # Carreras a la derecha

atributos = [n for n, d in G.nodes(data=True) if d["tipo"] == "atributo"]
for inst in instancias:
    # Buscar atributos conectados desde esta instancia
    attrs = [v for u, v in G.edges() if u == inst and G.nodes[v]["tipo"] == "atributo"]
    if not attrs:
        continue
    inst_x = pos[inst][0]
    # Distribuir atributos como "raíces" colgando de la instancia
    spread = 1.0
    start_x = inst_x - spread / 2
    step_x = spread / (len(attrs) - 1) if len(attrs) > 1 else 0
    for i, attr in enumerate(attrs):
        # Alternamos la Y ligeramente para que las cajas de texto no choquen entre sí
        pos[attr] = (start_x + i * step_x, 2 - (i % 2) * 0.4)



colores = []
tamanos = []

for n in G.nodes():
    if G.nodes[n]["tipo"] == "clase":
        colores.append("yellow")
        tamanos.append(2000)
    elif G.nodes[n]["tipo"] == "instancia":
        colores.append("#0b3d91") 
        tamanos.append(900)
    else:
        colores.append("green")
        tamanos.append(300)

plt.figure(figsize=(18, 12)) 

# Dibujar grafo base
nx.draw(G, pos, with_labels=True, node_color=colores, node_size=tamanos, edge_color="purple", font_size=7, font_color="black")

# Extraer y dibujar las etiquetas de las aristas ("tiene", "importante para")
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='purple', font_size=8)

plt.title("Ontología: Estructura y Relaciones", fontsize=16)
plt.show()