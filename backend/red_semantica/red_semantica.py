import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from clases import Alumno, BloqueAptitud, Carrera, Evaluacion


def configurar_ontologia():
    G = nx.DiGraph()

    # --- 1. CLASES BASE ---
    clases = ["Thing", "Persona", "Alumno", "Evaluacion", "Bloque/Aptitud", "Carrera"]
    G.add_nodes_from(clases, tipo="clase")

    G.add_edges_from([
        ("Persona", "Thing"),
        ("Carrera", "Thing"),
        ("Bloque/Aptitud", "Thing"),
        ("Evaluacion", "Thing"),
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
    a4 = Alumno("a4", "Juan Perez", "202304", "LIA")
    a5 = Alumno("a5", "Juan Perez", "202305", "ISC")
    alumnos = [a1, a2, a3, a4, a5]

    # --- 4. INSTANCIAS DE BLOQUES/APTITUDES ---
    aptitudes_base = [
        ("Calculo", c1), ("C. Fisico", c1), ("C. Biologico", c2),
        ("Mecanico", c3), ("Servicio social", c4), ("Literario", c4),
        ("Persuasivo", c2), ("Artistico", c4), ("Musical", c4),
        ("Situacion socioeconomica", c1)
    ]

    bloques = []
    relaciones_instancias = []

    for i, (nombre_apt, carrera_vinculada) in enumerate(aptitudes_base, 1):
        id_bloque = f"b{i}"
        nuevo_bloque = BloqueAptitud(id_bloque, nombre_apt)
        bloques.append(nuevo_bloque)
        relaciones_instancias.append((id_bloque, carrera_vinculada.get_id(), "importante para"))

    # --- 5. GENERACIÓN DINÁMICA DE EVALUACIONES ---
    evaluaciones = []
    id_eval_contador = 1

    for alumno in alumnos:
        for bloque in bloques:
            id_eval = f"e{id_eval_contador}"
            puntaje_simulado = random.randint(60, 100)

            nueva_eval = Evaluacion(id_eval, puntaje_simulado)
            evaluaciones.append(nueva_eval)

            # La evaluación ya no es un nodo: es una flecha Alumno -> Bloque con etiqueta
            relaciones_instancias.append(
                (alumno.get_id(), bloque.get_id(), f"evaluado ({puntaje_simulado})")
            )

            id_eval_contador += 1

    # --- 6. AGREGAR NODOS Y ATRIBUTOS AL GRAFO ---
    def agregar_nodos_y_atributos(entidades, nombre_clase, atributos_func, tipo_nodo="instancia"):
        for entidad in entidades:
            entidad_id = entidad.get_id()
            attrs = atributos_func(entidad)

            # Guardamos tipo y dataproperties directamente en el diccionario del nodo
            G.add_node(entidad_id, tipo=tipo_nodo, **attrs)
            G.add_edge(entidad_id, nombre_clase)

            # Creamos además nodos explícitos de atributos para visualización en grafo
            for clave, valor in attrs.items():
                nodo_attr = f"{clave}_{entidad_id}:{valor}"
                G.add_node(nodo_attr, tipo="atributo", clave=clave, valor=valor)
                G.add_edge(entidad_id, nodo_attr)

    # Función auxiliar para separar nombre completo en Nombre y Apellidos
    def extraer_datos_alumno(al):
        partes = al.get_nombre().strip().split(" ", 1)
        primer_nombre = partes[0] if partes else "Nulo"
        apellidos = partes[1] if len(partes) > 1 else "Nulo"

        # Obtener universidad si la clase la implementa, de lo contrario marcar 'Nulo'
        universidad = getattr(al, 'get_universidad', lambda: None)() or "Nulo"

        return {
            "nombre": primer_nombre,
            "apellidos": apellidos,
            "universidad": universidad,
            "no_control": al.get_no_control(),
            "carrera_sugerida": al.get_carrera_sugerida()
        }

    agregar_nodos_y_atributos(alumnos, "Alumno", extraer_datos_alumno)
    agregar_nodos_y_atributos(bloques, "Bloque/Aptitud", lambda b: {"nombre": b.get_nombre()})
    agregar_nodos_y_atributos(carreras, "Carrera", lambda c: {"nombre": c.get_nombre()})
    # Las evaluaciones ya no se agregan como nodos (ahora son flechas etiquetadas)

    for origen, destino, etiqueta in relaciones_instancias:
        G.add_edge(origen, destino, label=etiqueta)

    return G, alumnos, bloques, carreras, evaluaciones, relaciones_instancias


# --- 7. MÉTODO DE IMPRESIÓN ONTOLOGÍA COMPLETA ---
def imprimir_reporte_ontologia(alumnos, bloques, carreras, evaluaciones, relaciones_instancias):
    print("=" * 60)
    print(" " * 15 + "REPORTE DE DATOS DE LA ONTOLOGÍA")
    print("=" * 60)

    print("\n--- 1. INSTANCIAS DE ALUMNOS ---")
    for a in alumnos:
        print(f"[-] ID: {a.get_id():<4} | Nombre: {a.get_nombre()} | No. Control: {a.get_no_control()}")

    print("\n--- 2. INSTANCIAS DE BLOQUES FIJOS (Total: 10) ---")
    for b in bloques:
        print(f"[-] ID: {b.get_id():<4} | Nombre: {b.get_nombre()}")

    print("\n--- 3. EVALUACIONES DINÁMICAS (Muestra de 10 de 50) ---")
    for e in evaluaciones[:10]:
        print(f"[-] ID: {e.get_id():<4} | Puntaje: {e.get_puntaje()}")

    print("\n--- 4. RELACIONES (Muestra parcial) ---")
    dict_nombres = {
        **{a.get_id(): a.get_nombre() for a in alumnos},
        **{b.get_id(): b.get_nombre() for b in bloques},
        **{c.get_id(): c.get_nombre() for c in carreras},
        **{e.get_id(): f"Eval({e.get_puntaje()})" for e in evaluaciones}
    }

    for origen, destino, relacion in relaciones_instancias[:15]:
        nombre_origen = dict_nombres.get(origen, origen)
        nombre_destino = dict_nombres.get(destino, destino)
        print(f"{nombre_origen:<20} --( {relacion} )--> {nombre_destino}")

    print("\n" + "=" * 60)


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

    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True) if d.get("label")}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_color="#8A2BE2", font_size=6, label_pos=0.35)

    plt.title("Ontología Optimizada: Relaciones N-arias (punteros)", fontsize=18)
    plt.axis("off")
    plt.show()


def menu():
    print("\n" * 2, "\t= MENU DE OPCIONES =\n(1) Mostrar impresion de todos los alumnos con relaciones, bloques y carreras\n(2) Mostrar Grafo completo\n(3) Buscar alumno por No de control\n(4) Buscar alumno por Nombre\n(5) Salir...")


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

        # Determinar dirección de la arista
        relacion = ""
        if G.has_edge(alumno_id, vecino):
            relacion = f"--( {G.edges[alumno_id, vecino].get('label', 'conectado a')} )-->"
        else:
            relacion = f"<--( {G.edges[vecino, alumno_id].get('label', 'conectado por')} )--"

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

    edge_labels = nx.get_edge_attributes(sub_G, 'label')
    edge_labels_filtradas = {k: v for k, v in edge_labels.items() if v}
    nx.draw_networkx_edge_labels(sub_G, pos, edge_labels=edge_labels_filtradas,
                                 font_color='#8A2BE2', font_size=8)

    plt.title(f"Grafo de Vecinos Directos: {nombre_alumno} (NC: {no_control})", fontsize=15, fontweight='bold')
    plt.show()


# --- MÉTODOS DE BÚSQUEDA ---
def buscar(no_control, G, alumnos):
    alumno_id = None
    nombre_alumno = ""
    for a in alumnos:
        if a.get_no_control() == no_control:
            alumno_id = a.get_id()
            nombre_alumno = a.get_nombre()
            break

    if not alumno_id:
        print(f"\n[!] Error: No se encontró ningún alumno con el número de control '{no_control}'.")
        return

    graficar_subgrafo_alumno(alumno_id, nombre_alumno, no_control, G)


def buscar_por_nombre(nombre_buscar, G, alumnos):
    coincidencias = []

    for a in alumnos:
        if nombre_buscar.lower() in a.get_nombre().lower():
            coincidencias.append(a)

    if len(coincidencias) == 0:
        print(f"\n[!] Error: No se encontró ningún alumno que coincida con '{nombre_buscar}'.")
        return

    if len(coincidencias) == 1:
        alumno_encontrado = coincidencias[0]
        graficar_subgrafo_alumno(
            alumno_encontrado.get_id(),
            alumno_encontrado.get_nombre(),
            alumno_encontrado.get_no_control(),
            G
        )
        return

    print(f"\n[!] Se encontraron {len(coincidencias)} alumnos con ese nombre:")
    for indice, alumno in enumerate(coincidencias, start=1):
        print(f"    ({indice}) {alumno.get_nombre()} | No. Control: {alumno.get_no_control()} | Carrera: {alumno.get_carrera_sugerida()}")

    seleccion = input("\nSelecciona el número del alumno que quieres visualizar (o 'c' para cancelar): ")

    if seleccion.lower() == 'c':
        print("[*] Búsqueda cancelada.")
        return

    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(coincidencias)):
        print("[!] Selección inválida. Vuelve a intentar la búsqueda.")
        return

    alumno_elegido = coincidencias[int(seleccion) - 1]
    graficar_subgrafo_alumno(
        alumno_elegido.get_id(),
        alumno_elegido.get_nombre(),
        alumno_elegido.get_no_control(),
        G
    )


if __name__ == "__main__":
    G, alumnos, bloques, carreras, evaluaciones, relaciones = configurar_ontologia()
    op = "0"
    while op != "5":
        menu()
        op = input("\nusuario@> ")

        match op:
            case "1":
                print("*" * 150, "\nIMPRESION DE TODA LA RED\n")
                imprimir_reporte_ontologia(alumnos, bloques, carreras, evaluaciones, relaciones)

            case "2":
                print("*" * 150, "\nGRAFO COMPLETO\n")
                visualizar_grafo(G)

            case "3":
                print("*" * 150, "\nBUSQUEDA DE ALUMNO POR NUMERO DE CONTROL\n")
                nc = input("\nIngresa el número de control del alumno a buscar (ej. 202301): ")
                buscar(nc, G, alumnos)

            case "4":
                print("*" * 150, "\nBUSQUEDA DE ALUMNO POR NOMBRE\n")
                nombre = input("\nIngresa el nombre del alumno a buscar (ej. Juan): ")
                buscar_por_nombre(nombre, G, alumnos)

            case "5":
                print("Saliendo del sistema...")
                time.sleep(2.5)
                print("Adios...")
            case _:
                print("Opcion no valida. Vuelve a intentarlo")
                op = "0"