"""Construcción de la ontología (grafo dirigido con networkx)."""
import random
import networkx as nx
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
    # Cada relación es una tupla: (origen, destino, etiqueta, data_properties_de_la_relacion)
    relaciones_instancias = []

    for i, (nombre_apt, carrera_vinculada) in enumerate(aptitudes_base, 1):
        id_bloque = f"b{i}"
        nuevo_bloque = BloqueAptitud(id_bloque, nombre_apt)
        bloques.append(nuevo_bloque)
        relaciones_instancias.append((id_bloque, carrera_vinculada.get_id(), "importante para", {}))

    # Relación Alumno -> Carrera (carrera sugerida), enlazada por siglas "(ICO)", "(LIA)"...
    carrera_por_sigla = {c.get_nombre().split("(")[-1].rstrip(")"): c for c in carreras}
    for alumno in alumnos:
        carrera = carrera_por_sigla.get(alumno.get_carrera_sugerida())
        if carrera:
            relaciones_instancias.append((alumno.get_id(), carrera.get_id(), "carrera sugerida", {}))

    # --- 5. GENERACIÓN DINÁMICA DE EVALUACIONES ---
    evaluaciones = []
    id_eval_contador = 1

    for alumno in alumnos:
        for bloque in bloques:
            id_eval = f"e{id_eval_contador}"
            puntaje_simulado = random.randint(60, 100)

            nueva_eval = Evaluacion(id_eval, puntaje_simulado)
            evaluaciones.append(nueva_eval)

            # Flecha Alumno -> Bloque; el puntaje es data property de la relación
            relaciones_instancias.append(
                (alumno.get_id(), bloque.get_id(), "evaluado", {"puntaje": puntaje_simulado})
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

    # Las data properties de la relación (ej. puntaje) quedan como atributos de la arista
    for origen, destino, etiqueta, props in relaciones_instancias:
        G.add_edge(origen, destino, label=etiqueta, **props)

    return G, alumnos, bloques, carreras, evaluaciones, relaciones_instancias
