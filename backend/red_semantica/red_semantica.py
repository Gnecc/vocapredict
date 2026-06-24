import networkx as nx
import matplotlib.pyplot as plt
import random # Usado para generar puntajes de ejemplo rápidamente
from clases import Alumno, BloqueAptitud, Carrera

def configurar_ontologia():
    G = nx.DiGraph()

    # --- 1. CLASES BASE ---
    clases = ["Thing", "Persona", "Alumno", "Bloque/Aptitud", "Carrera"]
    G.add_nodes_from(clases, tipo="clase")
    
    G.add_edges_from([
        ("Persona", "Thing"),
        ("Carrera", "Thing"),
        ("Bloque/Aptitud", "Thing"),
        ("Alumno", "Persona")
    ])

    # --- 2. INSTANCIAS DE CARRERAS ---
    c1 = Carrera("c1", "Ingenieria en Computacion (ICO)")
    c2 = Carrera("c2", "Licenciatura en Informatica Administrativa (LIA)")
    c3 = Carrera("c3", "Ingenieria en Sistemas Inteligentes (ISC)")
    c4 = Carrera("c4", "Licenciatura en Lenguas (LLE)")
    carreras = [c1, c2, c3, c4]

    # --- 3. INSTANCIAS DE ALUMNOS ---
    a1 = Alumno("a1", "Juan Perez", "202301", "ICO")
    a2 = Alumno("a2", "Maria Lopez", "202302", "ISC")
    a3 = Alumno("a3", "Carlos Ruiz", "202303", "LIA")
    alumnos = [a1, a2, a3]

    # --- 4. GENERACIÓN DINÁMICA DE BLOQUES POR ALUMNO ---
    # Estructura: (Nombre de Aptitud, Carrera a la que es importante)
    aptitudes_base = [
        ("Calculo", c1), ("C. Fisico", c1), ("C. Biologico", c2),
        ("Mecanico", c3), ("Servicio social", c4), ("Literario", c4),
        ("Persuasivo", c2), ("Artistico", c4), ("Musical", c4),
        ("Situacion socioeconomica", c1)
    ]

    bloques = []
    relaciones_instancias = []
    id_contador = 1

    for alumno in alumnos:
        for nombre_apt, carrera_vinculada in aptitudes_base:
            # Crear ID único, ej: b1, b2... b30
            id_bloque = f"b{id_contador}"
            
            # NOTA: Usamos un random para simular los puntajes.
            # Se puede sustituir esto leyendo de un JSON o lista si se tienen definidos.
            puntaje_simulado = random.randint(60, 100) 
            
            nuevo_bloque = BloqueAptitud(id_bloque, nombre_apt, puntaje_simulado)
            bloques.append(nuevo_bloque)
            
            # Automatizamos las relaciones aquí mismo
            relaciones_instancias.append((alumno.get_id(), id_bloque, "tiene"))
            relaciones_instancias.append((id_bloque, carrera_vinculada.get_id(), "importante para"))
            
            id_contador += 1

    # --- 5. AGREGAR NODOS Y ATRIBUTOS AL GRAFO ---
    def agregar_nodos_y_atributos(entidades, nombre_clase, atributos_func):
        for entidad in entidades:
            G.add_node(entidad.get_id(), tipo="instancia")
            G.add_edge(entidad.get_id(), nombre_clase)
            
            for clave, valor in atributos_func(entidad).items():
                nodo_attr = f"{clave}_{entidad.get_id()}:{valor}"
                G.add_node(nodo_attr, tipo="atributo")
                G.add_edge(entidad.get_id(), nodo_attr)

    agregar_nodos_y_atributos(alumnos, "Alumno", lambda a: {"nombre": a.get_nombre(), "nc": a.get_no_control(), "cs": a.get_carrera_sugerida()})
    agregar_nodos_y_atributos(bloques, "Bloque/Aptitud", lambda b: {"nombre": b.get_nombre(), "puntaje": b.get_puntaje()})
    agregar_nodos_y_atributos(carreras, "Carrera", lambda c: {"nombre": c.get_nombre()})

    for origen, destino, etiqueta in relaciones_instancias:
        G.add_edge(origen, destino, label=etiqueta)

    return G, alumnos, bloques, carreras, relaciones_instancias

# --- 6. MÉTODO DE IMPRESIÓN SOLICITADO ---
def imprimir_reporte_ontologia(alumnos, bloques, carreras, relaciones_instancias):
    print("=" * 60)
    print(" " * 15 + "REPORTE DE DATOS DE LA ONTOLOGÍA")
    print("=" * 60)

    print("\n--- 1. INSTANCIAS DE ALUMNOS Y SUS DATOS ---")
    for a in alumnos:
        print(f"[-] ID: {a.get_id():<4} | Nombre: {a.get_nombre():<12} | No. Control: {a.get_no_control():<8} | Carrera Sugerida: {a.get_carrera_sugerida()}")

    print("\n--- 2. INSTANCIAS DE BLOQUES/APTITUDES Y SUS DATOS (Muestra de 10) ---")
    for b in bloques[:10]: # Solo mostramos 10 para no saturar la consola
        print(f"[-] ID: {b.get_id():<4} | Nombre: {b.get_nombre():<25} | Puntaje: {b.get_puntaje()}")
    print("... (Se generaron 30 en total)")

    print("\n--- 3. INSTANCIAS DE CARRERAS ---")
    for c in carreras:
        print(f"[-] ID: {c.get_id():<4} | Nombre: {c.get_nombre()}")

    print("\n--- 4. RELACIONES ENTRE INSTANCIAS (Muestra) ---")
    dict_alumnos = {a.get_id(): a.get_nombre() for a in alumnos}
    dict_bloques = {b.get_id(): b.get_nombre() for b in bloques}
    dict_carreras = {c.get_id(): c.get_nombre() for c in carreras}

    for origen, destino, relacion in relaciones_instancias[:15]: # Muestra parcial
        if relacion == "tiene":
            nombre_origen = dict_alumnos.get(origen, origen)
            nombre_destino = dict_bloques.get(destino, destino)
            print(f"[Alumno] {nombre_origen:<12} --( {relacion} )--> [Bloque] {nombre_destino}")
        elif relacion == "importante para":
            nombre_origen = dict_bloques.get(origen, origen)
            nombre_destino = dict_carreras.get(destino, destino)
            print(f"[Bloque] {nombre_origen:<25} --( {relacion} )--> [Carrera] {nombre_destino}")

    print("\n" + "=" * 60)

# --- 7. DIBUJADO DEL GRAFO ---
def visualizar_grafo(G):
    pos = {
        "Thing": (5, 7),
        "Persona": (2, 6),
        "Bloque/Aptitud": (5, 6),
        "Carrera": (8, 6),
        "Alumno": (2, 5)
    }

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

    # Ampliamos el espacio para los bloques en el eje X ya que ahora son 30
    asignar_eje_x(inst_a, 0.5, 3.5, 4) 
    asignar_eje_x(inst_b, 1.0, 9.0, 3) # Mucho más ancho para que quepan los 30 nodos
    asignar_eje_x(inst_c, 6.5, 9.5, 4) 

    # Posicionar atributos debajo de sus instancias
    for inst in instancias:
        attrs = [v for u, v in G.edges() if u == inst and G.nodes[v].get("tipo") == "atributo"]
        if not attrs: continue
        inst_x = pos[inst][0]
        spread = 0.8
        start_x = inst_x - spread / 2
        step_x = spread / (len(attrs) - 1) if len(attrs) > 1 else 0
        for i, attr in enumerate(attrs):
            pos[attr] = (start_x + i * step_x, pos[inst][1] - 0.5 - (i % 2) * 0.3)

    colores = []
    tamanos = []
    for n in G.nodes():
        if G.nodes[n].get("tipo") == "clase":
            colores.append("yellow")
            tamanos.append(2000)
        elif G.nodes[n].get("tipo") == "instancia":
            colores.append("#0b3d91")  
            tamanos.append(900)
        else:
            colores.append("green")
            tamanos.append(200) # Ligeramente más pequeños para no saturar

    plt.figure(figsize=(20, 14)) # Lienzo más grande
    nx.draw(G, pos, with_labels=True, node_color=colores, node_size=tamanos, edge_color="purple", font_size=6, font_color="black")

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='purple', font_size=7)

    plt.title("Ontología: Estructura y Relaciones Dinámicas", fontsize=16)
    plt.show()

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    G, alumnos, bloques, carreras, relaciones = configurar_ontologia()
    imprimir_reporte_ontologia(alumnos, bloques, carreras, relaciones)
    visualizar_grafo(G)