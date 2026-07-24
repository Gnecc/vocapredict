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
        ("Evaluacion", "Thing"), # Conectamos la nueva clase a Thing
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

    # --- 4. INSTANCIAS DE BLOQUES/APTITUDES (AHORA SON 10 FIJOS) ---
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
        
        # Esta relación hacia la carrera se crea UNA SOLA VEZ por bloque
        relaciones_instancias.append((id_bloque, carrera_vinculada.get_id(), "importante para"))

    # --- 5. GENERACIÓN DINÁMICA DE EVALUACIONES (La solución) ---
    evaluaciones = []
    id_eval_contador = 1

    for alumno in alumnos:
        for bloque in bloques:
            id_eval = f"e{id_eval_contador}"
            puntaje_simulado = random.randint(60, 100) 
            
            nueva_eval = Evaluacion(id_eval, puntaje_simulado)
            evaluaciones.append(nueva_eval)
            
            # El alumno TIENE una evaluación
            relaciones_instancias.append((alumno.get_id(), id_eval, "tiene"))
            # La evaluación PERTENECE A un bloque global
            relaciones_instancias.append((id_eval, bloque.get_id(), "pertenece a"))
            
            id_eval_contador += 1

    # --- 6. AGREGAR NODOS Y ATRIBUTOS AL GRAFO ---
    def agregar_nodos_y_atributos(entidades, nombre_clase, atributos_func):
        for entidad in entidades:
            G.add_node(entidad.get_id(), tipo="instancia")
            G.add_edge(entidad.get_id(), nombre_clase)
            
            for clave, valor in atributos_func(entidad).items():
                nodo_attr = f"{clave}_{entidad.get_id()}:{valor}"
                G.add_node(nodo_attr, tipo="atributo")
                G.add_edge(entidad.get_id(), nodo_attr)

    agregar_nodos_y_atributos(alumnos, "Alumno", lambda a: {"nombre": a.get_nombre(), "nc": a.get_no_control(), "cs": a.get_carrera_sugerida()})
    agregar_nodos_y_atributos(bloques, "Bloque/Aptitud", lambda b: {"nombre": b.get_nombre()})
    agregar_nodos_y_atributos(carreras, "Carrera", lambda c: {"nombre": c.get_nombre()})
    # Agregamos los nodos de evaluaciones y su atributo de puntaje
    agregar_nodos_y_atributos(evaluaciones, "Evaluacion", lambda e: {"puntaje": e.get_puntaje()})

    for origen, destino, etiqueta in relaciones_instancias:
        G.add_edge(origen, destino, label=etiqueta)

    return G, alumnos, bloques, carreras, evaluaciones, relaciones_instancias

# --- 7. MÉTODO DE IMPRESIÓN ---
def imprimir_reporte_ontologia(alumnos, bloques, carreras, evaluaciones, relaciones_instancias):
    print("=" * 60)
    print(" " * 15 + "REPORTE DE DATOS DE LA ONTOLOGÍA")
    print("=" * 60)

    print("\n--- 1. INSTANCIAS DE ALUMNOS ---")
    for a in alumnos:
        print(f"[-] ID: {a.get_id():<4} | Nombre: {a.get_nombre()}")

    print("\n--- 2. INSTANCIAS DE BLOQUES FIJOS (Total: 10) ---")
    for b in bloques:
        print(f"[-] ID: {b.get_id():<4} | Nombre: {b.get_nombre()}")

    print("\n--- 3. EVALUACIONES DINÁMICAS (Muestra de 10 de 30) ---")
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

# --- 8. DIBUJADO DEL GRAFO ---
def visualizar_grafo(G):
    # Reestructuramos la posición para acomodar la capa intermedia
    pos = {
        "Thing": (5, 8),
        "Persona": (2, 7),
        "Evaluacion": (5, 7),
        "Bloque/Aptitud": (7, 7),
        "Carrera": (9, 7),
        "Alumno": (2, 6)
    }

    instancias = [n for n, d in G.nodes(data=True) if d["tipo"] == "instancia"]
    inst_a = sorted([n for n in instancias if n.startswith("a")])
    inst_e = sorted([n for n in instancias if n.startswith("e")], key=lambda x: int(x[1:]))
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

    # Distribuimos las instancias en diferentes alturas
    asignar_eje_x(inst_a, 1.0, 3.0, 4) 
    asignar_eje_x(inst_e, 0.5, 9.5, 3) # Capa intermedia de evaluaciones (30 nodos)
    asignar_eje_x(inst_b, 1.5, 8.5, 2) # Capa de 10 bloques globales
    asignar_eje_x(inst_c, 3.0, 7.0, 1) # Carreras en la base

    # Atributos
    for inst in instancias:
        attrs = [v for u, v in G.edges() if u == inst and G.nodes[v].get("tipo") == "atributo"]
        if not attrs: continue
        inst_x = pos[inst][0]
        spread = 0.6
        start_x = inst_x - spread / 2
        step_x = spread / (len(attrs) - 1) if len(attrs) > 1 else 0
        for i, attr in enumerate(attrs):
            pos[attr] = (start_x + i * step_x, pos[inst][1] - 0.4 - (i % 2) * 0.2)

    colores = []
    tamanos = []
    for n in G.nodes():
        if G.nodes[n].get("tipo") == "clase":
            colores.append("yellow")
            tamanos.append(2000)
        elif G.nodes[n].get("tipo") == "instancia":
            # Diferenciamos un poco los colores de las instancias
            if str(n).startswith('e'): colores.append("#8A2BE2") # Evaluaciones en morado
            else: colores.append("#0b3d91") # Resto azul
            tamanos.append(700 if str(n).startswith('e') else 1000)
        else:
            colores.append("green")
            tamanos.append(200)

    plt.figure(figsize=(22, 16)) 
    nx.draw(G, pos, with_labels=True, node_color=colores, node_size=tamanos, edge_color="gray", font_size=6, font_color="black")

    edge_labels = nx.get_edge_attributes(G, 'label')
    # Solo dibujamos etiquetas de relaciones principales para no ensuciar la red
    edge_labels_filtradas = {k: v for k, v in edge_labels.items() if v in ["tiene", "pertenece a", "importante para"]}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_filtradas, font_color='purple', font_size=7)

    plt.title("Ontología Optimizada: Relaciones N-arias", fontsize=18)
    plt.show()

#metodo para mostrar las opciones:
def menu():
    print("\n"*2,"\t= MENU DE OPCIONES =\n(1) Mostrar imprecion de todos los alumnos con relaciones, bloques y carreras\n(2) Mostrar Grafo completo\n(3) Buscar alumno por No de control\n(4) Buscar alumno por Nombre\n(5) Salir...")

#Metodo para buscar alumno
def buscar(no_control, G, alumnos):
    #Buscar el ID del alumno usando su número de control
    alumno_id = None
    nombre_alumno = ""
    for a in alumnos:
        if a.get_no_control() == no_control:
            alumno_id = a.get_id()
            nombre_alumno = a.get_nombre()
            break
            
    #Validar si el alumno existe
    if not alumno_id:
        print(f"\n[!] Error: No se encontró ningún alumno con el número de control '{no_control}'.")
        return

    print(f"\n[*] Generando grafo para el alumno: {nombre_alumno} ({alumno_id})...")

    #Obtener todos los nodos relacionados (descendientes en el grafo dirigido)
    # Esto traerá sus atributos, evaluaciones, bloques, carreras y clases de la ontología
    nodos_relacionados = list(nx.descendants(G, alumno_id))
    nodos_relacionados.append(alumno_id) # Agregamos también el nodo del alumno principal

    #Crear un subgrafo solo con estos nodos
    sub_G = G.subgraph(nodos_relacionados)

    #Configurar la visualización del subgrafo
    plt.figure(figsize=(14, 10))
    
    #Usamos un layout de resorte (spring_layout) que se adapta muy bien a subgrafos pequeños
    pos = nx.spring_layout(sub_G, seed=42, k=0.5)

    colores = []
    tamanos = []
    
    #Asignar colores y tamaños dependiendo del tipo de nodo
    for n in sub_G.nodes():
        tipo = sub_G.nodes[n].get("tipo")
        
        if n == alumno_id:
            colores.append("red") # Resaltamos al alumno buscado en ROJO
            tamanos.append(1500)
        elif tipo == "clase":
            colores.append("yellow")
            tamanos.append(1500)
        elif tipo == "instancia":
            if str(n).startswith('e'): 
                colores.append("#8A2BE2") # Evaluaciones en morado
            elif str(n).startswith('c'):
                colores.append("#ff8c00") # Carreras en naranja
            else: 
                colores.append("#0b3d91") # Bloques en azul oscuro
            tamanos.append(800)
        else: # Atributos (tipo == "atributo")
            colores.append("lightgreen")
            tamanos.append(400)

    #Dibujar los nodos y aristas
    nx.draw(sub_G, pos, with_labels=True, node_color=colores, 
            node_size=tamanos, edge_color="gray", font_size=8, font_weight="bold")

    #Dibujar las etiquetas de las relaciones principales
    edge_labels = nx.get_edge_attributes(sub_G, 'label')
    edge_labels_filtradas = {k: v for k, v in edge_labels.items() if v} # Filtrar aristas sin label
    nx.draw_networkx_edge_labels(sub_G, pos, edge_labels=edge_labels_filtradas, font_color='red', font_size=7)

    plt.title(f"Grafo de Relaciones: {nombre_alumno} (NC: {no_control})", fontsize=16, fontweight='bold')
    plt.show()    

def buscar_por_nombre(nombre_buscar, G, alumnos):
    # En lugar de guardar uno solo, creamos una lista para guardar todas las coincidencias
    coincidencias = []
    
    for a in alumnos:
        if nombre_buscar.lower() in a.get_nombre().lower():
            coincidencias.append(a)
            
    # Caso 1: No encontró a nadie
    if len(coincidencias) == 0:
        print(f"\n[!] Error: No se encontró ningún alumno que coincida con '{nombre_buscar}'.")
        return
        
    # Caso 2: Encontró a más de un alumno (¡Tu caso de los dos Juanes!)
    if len(coincidencias) > 1:
        print(f"\n[!] Se encontraron {len(coincidencias)} alumnos con ese nombre. Por favor sé más específico:")
        for alumno in coincidencias:
            print(f"    - {alumno.get_nombre()} (No. Control: {alumno.get_no_control()})")
        print("\n[*] Intenta buscar de nuevo escribiendo el apellido, o usa la opción 3 (Número de control).")
        return

    # Caso 3: Encontró exactamente a uno (Todo sale bien)
    alumno_encontrado = coincidencias[0]
    alumno_id = alumno_encontrado.get_id()
    nombre_alumno = alumno_encontrado.get_nombre()
    no_control = alumno_encontrado.get_no_control()

    print(f"\n[*] Generando grafo para el alumno: {nombre_alumno} ({alumno_id})...")

    # --- Reutilizamos tu misma lógica de dibujado del subgrafo ---
    nodos_relacionados = list(nx.descendants(G, alumno_id))
    nodos_relacionados.append(alumno_id)

    sub_G = G.subgraph(nodos_relacionados)
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(sub_G, seed=42, k=0.5)

    colores = []
    tamanos = []
    
    for n in sub_G.nodes():
        tipo = sub_G.nodes[n].get("tipo")
        if n == alumno_id:
            colores.append("red") 
            tamanos.append(1500)
        elif tipo == "clase":
            colores.append("yellow")
            tamanos.append(1500)
        elif tipo == "instancia":
            if str(n).startswith('e'): colores.append("#8A2BE2") 
            elif str(n).startswith('c'): colores.append("#ff8c00") 
            else: colores.append("#0b3d91") 
            tamanos.append(800)
        else: 
            colores.append("lightgreen")
            tamanos.append(400)

    nx.draw(sub_G, pos, with_labels=True, node_color=colores, node_size=tamanos, edge_color="gray", font_size=8, font_weight="bold")
    edge_labels = nx.get_edge_attributes(sub_G, 'label')
    edge_labels_filtradas = {k: v for k, v in edge_labels.items() if v} 
    nx.draw_networkx_edge_labels(sub_G, pos, edge_labels=edge_labels_filtradas, font_color='red', font_size=7)

    plt.title(f"Grafo de Relaciones: {nombre_alumno} (NC: {no_control})", fontsize=16, fontweight='bold')
    plt.show()

if __name__ == "__main__":
    G, alumnos, bloques, carreras, evaluaciones, relaciones = configurar_ontologia()
    op = "0"
    while op != "5":
        menu()
        op = input("\nusuario@> ")
    
        match op:
            case "1":
                print("*"*150,"\nIMPRECION DE TODA LA RED\n")
                imprimir_reporte_ontologia(alumnos, bloques, carreras, evaluaciones, relaciones)

            case "2":
                print("*"*150,"\nGRAFO COMPLETO\n")
                visualizar_grafo(G)

            case "3":
                print("*"*150,"\nBUSQUEDA DE ALUMNO\n")
                nc = input("\nIngresa el número de control del alumno a buscar (ej. 202301): ")
                # Pasamos G y alumnos como parámetros
                buscar(nc, G, alumnos)
                
            case "4":
                print("*"*150,"\nBUSQUEDA DE ALUMNO POR NOMBRE\n")
                nombre = input("\nIngresa el nombre del alumno a buscar (ej. Juan): ")
                buscar_por_nombre(nombre, G, alumnos)
                
            case "5":
                print("Saliendo del sistema...")
                time.sleep(3.5)
                print("Adios...")
            case _:
                print("Opcion no valida. Vuelve a intentarlo")
                op = "0"
    
    
    


