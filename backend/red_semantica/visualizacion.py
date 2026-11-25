"""Dibujado del grafo completo y del subgrafo de un alumno."""
import networkx as nx
import matplotlib.pyplot as plt
from utils import formato_relacion


# --- 8. DIBUJADO DEL GRAFO COMPLETO ---
def visualizar_grafo(G):
    pos = {
        "Thing": (5, 8),
        "Persona": (2, 7),
        "Evaluacion": (5, 7),
        "Bloque/Aptitud": (7, 7),
        "Carrera": (9, 7),
        "Alumno": (2, 6)
    }

    instancias = [n for n, d in G.nodes(data=True) if d.get("tipo") == "instancia"]
    inst_a = sorted([n for n in instancias if n.startswith("a")])
    inst_b = sorted([n for n in instancias if n.startswith("b")], key=lambda x: int(x[1:]))
    inst_c = sorted([n for n in instancias if n.startswith("c")])

    def asignar_eje_x(nodos, start_x, end_x, y):
        if not nodos:
            return
        if len(nodos) == 1:
            pos[nodos[0]] = ((start_x + end_x) / 2, y)
            return
        step = (end_x - start_x) / (len(nodos) - 1)
        for i, nodo in enumerate(nodos):
            pos[nodo] = (start_x + i * step, y)

    asignar_eje_x(inst_a, 1.0, 5.0, 4)
    asignar_eje_x(inst_b, 0.5, 9.5, 2)
    asignar_eje_x(inst_c, 3.0, 7.0, 0)

    for inst in instancias:
        attrs = [v for u, v in G.edges() if u == inst and G.nodes[v].get("tipo") == "atributo"]
        if not attrs:
            continue
        inst_x = pos[inst][0]
        spread = 0.6
        start_x = inst_x - spread / 2
        step_x = spread / (len(attrs) - 1) if len(attrs) > 1 else 0
        for i, attr in enumerate(attrs):
            pos[attr] = (start_x + i * step_x, pos[inst][1] - 0.4 - (i % 2) * 0.2)

    nodos = list(G.nodes())
    colores, tamanos = [], []
    for n in nodos:
        tipo = G.nodes[n].get("tipo")
        if tipo == "clase":
            colores.append("yellow")
            tamanos.append(2000)
        elif tipo == "instancia":
            colores.append("#0b3d91")
            tamanos.append(1000)
        else:
            colores.append("green")
            tamanos.append(200)

    # Separar flechas de relación (con etiqueta) de las demás aristas
    aristas_relacion = [(u, v) for u, v, d in G.edges(data=True) if d.get("label")]
    aristas_otras = [e for e in G.edges() if e not in aristas_relacion]

    plt.figure(figsize=(22, 16))
    nx.draw_networkx_nodes(G, pos, nodelist=nodos, node_color=colores, node_size=tamanos)
    nx.draw_networkx_labels(G, pos, font_size=6, font_color="black")

    nx.draw_networkx_edges(G, pos, edgelist=aristas_otras, edge_color="gray",
                           arrows=True, arrowsize=10, node_size=tamanos)
    # Punteros (flechas moradas) con su etiqueta de relación
    nx.draw_networkx_edges(G, pos, edgelist=aristas_relacion, edge_color="#8A2BE2",
                           width=1.2, arrows=True, arrowstyle="-|>", arrowsize=18,
                           node_size=tamanos)

    edge_labels = {(u, v): formato_relacion(d["label"], {k: val for k, val in d.items() if k != "label"})
                   for u, v, d in G.edges(data=True) if d.get("label")}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_color="#8A2BE2", font_size=6, label_pos=0.35)

    plt.title("Ontología Optimizada: Relaciones N-arias (punteros)", fontsize=18)
    plt.axis("off")
    plt.show()


# --- FUNCIÓN MEJORADA: CONSULTA DE VECINOS, DATAPROPERTIES Y DIBUJO DE SUBGRAFO ---
def graficar_subgrafo_alumno(alumno_id, nombre_alumno, no_control, G):
    print(f"\n[*] Generando consulta y subgrafo para el alumno ID: {alumno_id}...")

    # 1. Obtener los vecinos más cercanos (predecesores y sucesores directos)
    vecinos_directos = set(nx.all_neighbors(G, alumno_id))

    # 2. Definir el conjunto de nodos del subgrafo: Alumno + Sus Atributos + Vecinos Directos + Atributos de Vecinos
    nodos_subgrafo = set([alumno_id] + list(vecinos_directos))
    for v in list(vecinos_directos):
        # Añadimos los atributos de los vecinos para mostrar su información completa
        nodos_subgrafo.update(G.successors(v))

    sub_G = G.subgraph(nodos_subgrafo)

    # 3. IMPRESIÓN DE DATAPROPERTIES EN CONSOLA
    print("\n" + "=" * 65)
    print(f" DATAPROPERTIES DEL ALUMNO CONSULTADO ({alumno_id})")
    print("=" * 65)

    datos_nodo = G.nodes[alumno_id]
    print(f"  • Nombre           : {datos_nodo.get('nombre', 'Nulo')}")
    print(f"  • Apellidos        : {datos_nodo.get('apellidos', 'Nulo')}")
    print(f"  • Universidad      : {datos_nodo.get('universidad', 'Nulo')}")
    print(f"  • No. Control (ID) : {datos_nodo.get('no_control', no_control)}")
    print(f"  • Carrera Sugerida : {datos_nodo.get('carrera_sugerida', 'Nulo')}")

    print("\n" + "-" * 65)
    print(" DATAPROPERTIES DE LOS VECINOS MÁS CERCANOS")
    print("-" * 65)

    for vecino in vecinos_directos:
        tipo_vecino = G.nodes[vecino].get("tipo", "Desconocido")

        # Determinar dirección de la arista y data properties de la relación (ej. puntaje)
        if G.has_edge(alumno_id, vecino):
            datos_arista = G.edges[alumno_id, vecino]
            props_relacion = {k: v for k, v in datos_arista.items() if k != "label"}
            relacion = f"-- {formato_relacion(datos_arista.get('label', 'conectado a'), props_relacion)} -->"
        else:
            datos_arista = G.edges[vecino, alumno_id]
            props_relacion = {k: v for k, v in datos_arista.items() if k != "label"}
            relacion = f"<-- {formato_relacion(datos_arista.get('label', 'conectado por'), props_relacion)} --"

        # Recopilar los atributos del vecino
        props_vecino = []
        for _, attr_node in G.out_edges(vecino):
            if G.nodes[attr_node].get("tipo") == "atributo":
                c = G.nodes[attr_node].get("clave", "")
                val = G.nodes[attr_node].get("valor", "")
                props_vecino.append(f"{c}: {val}")

        info_props = ", ".join(props_vecino) if props_vecino else "Sin data properties extras"
        print(f"  • [{vecino}] {relacion} {tipo_vecino.upper()} | Properties: {info_props}")

    print("=" * 65 + "\n")

    # 4. DIBUJAR EL GRAFO TRAS COMPLETAR LA BÚSQUEDA
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(sub_G, seed=42, k=0.6)

    colores = []
    tamanos = []

    for n in sub_G.nodes():
        tipo = sub_G.nodes[n].get("tipo")

        if n == alumno_id:
            colores.append("red")          # Resaltamos al alumno buscado en ROJO
            tamanos.append(1600)
        elif tipo == "clase":
            colores.append("yellow")
            tamanos.append(1400)
        elif tipo == "instancia":
            if str(n).startswith('c'):
                colores.append("#ff8c00")  # Carreras en naranja
            elif str(n).startswith('b'):
                colores.append("#0b3d91")  # Bloques en azul oscuro
            else:
                colores.append("cyan")
            tamanos.append(800)
        else:  # Atributos (tipo == "atributo")
            colores.append("lightgreen")
            tamanos.append(400)

    nx.draw(sub_G, pos, with_labels=True, node_color=colores,
            node_size=tamanos, edge_color="gray", font_size=8, font_weight="bold",
            arrows=True, arrowsize=20)

    edge_labels_filtradas = {
        (u, v): formato_relacion(d["label"], {k: val for k, val in d.items() if k != "label"})
        for u, v, d in sub_G.edges(data=True) if d.get("label")
    }
    nx.draw_networkx_edge_labels(sub_G, pos, edge_labels=edge_labels_filtradas,
                                 font_color='#8A2BE2', font_size=8)

    plt.title(f"Grafo de Vecinos Directos: {nombre_alumno} (NC: {no_control})", fontsize=15, fontweight='bold')
    plt.show()
