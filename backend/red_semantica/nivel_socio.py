"""Demo de consulta por nivel socioeconómico."""
import matplotlib.pyplot as plt
from config import NOMBRE_BLOQUE_SOCIO, NIVELES_SOCIO, COLORES_NIVEL
from utils import nombre_nodo


# --- DEMO: CONSULTA POR NIVEL SOCIOECONÓMICO ---
def clasificar_nivel_socio(puntaje):
    """Convierte un puntaje en nivel socioeconómico (Bajo / Medio / Alto)."""
    for nombre, minimo, maximo in NIVELES_SOCIO:
        if minimo <= puntaje <= maximo:
            return nombre
    return "Sin clasificar"


def obtener_niveles_socio(G):
    """Devuelve [(alumno_id, puntaje, nivel)] leyendo las flechas 'evaluado'
    que llegan al bloque 'Situacion socioeconomica'."""
    bloque_id = next((n for n, d in G.nodes(data=True)
                      if d.get("tipo") == "instancia" and d.get("nombre") == NOMBRE_BLOQUE_SOCIO), None)
    if bloque_id is None:
        return []

    resultados = []
    for u, _, d in G.in_edges(bloque_id, data=True):
        if d.get("label") == "evaluado" and "puntaje" in d:
            resultados.append((u, d["puntaje"], clasificar_nivel_socio(d["puntaje"])))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados


def consulta_por_nivel_socioeconomico(G, nivel):
    """Lista los alumnos que pertenecen a un nivel socioeconómico dado."""
    datos = [r for r in obtener_niveles_socio(G) if r[2].lower() == nivel.lower()]
    rango = next((f"{mn}-{mx}" for nom, mn, mx in NIVELES_SOCIO if nom.lower() == nivel.lower()), "?")

    print(f"\n--- NIVEL SOCIOECONÓMICO {nivel.upper()} (puntaje {rango}) | {len(datos)} alumno(s) ---")
    if not datos:
        print("  (ningún alumno en este nivel)")
        return datos

    for alumno_id, puntaje, _ in datos:
        carrera = G.nodes[alumno_id].get("carrera_sugerida", "Nulo")
        nc = G.nodes[alumno_id].get("no_control", "Nulo")
        print(f"  [{alumno_id}] {nombre_nodo(G, alumno_id):<14} | NC: {nc} | "
              f"Puntaje: {puntaje:<3} | Carrera sugerida: {carrera}")
    return datos


def consulta_todos_los_niveles(G):
    """Lista a todos los alumnos con su puntaje y nivel socioeconómico (de mayor a menor puntaje)."""
    datos = obtener_niveles_socio(G)
    print(f"\n--- TODOS LOS NIVELES SOCIOECONÓMICOS | {len(datos)} alumno(s) ---")
    for alumno_id, puntaje, nivel in datos:
        carrera = G.nodes[alumno_id].get("carrera_sugerida", "Nulo")
        nc = G.nodes[alumno_id].get("no_control", "Nulo")
        print(f"  [{alumno_id}] {nombre_nodo(G, alumno_id):<14} | NC: {nc} | "
              f"Puntaje: {puntaje:<3} | Nivel: {nivel:<5} | Carrera sugerida: {carrera}")
    return datos


def menu_nivel_socio():
    print("\n\t= SUBMENU: NIVEL SOCIOECONÓMICO =")
    for i, (nombre, mn, mx) in enumerate(NIVELES_SOCIO, 1):
        print(f"({i}) Ver solo nivel {nombre} (puntaje {mn}-{mx})")
    print(f"({len(NIVELES_SOCIO) + 1}) Ver todos")
    print(f"({len(NIVELES_SOCIO) + 2}) Volver al menú principal")


def submenu_nivel_socioeconomico(G):
    """Submenú: ver solo Bajo, solo Medio, solo Alto o todos los alumnos."""
    if not obtener_niveles_socio(G):
        print(f"\n[!] No se encontró el bloque '{NOMBRE_BLOQUE_SOCIO}' en el grafo.")
        return

    opcion_todos = str(len(NIVELES_SOCIO) + 1)
    opcion_volver = str(len(NIVELES_SOCIO) + 2)
    opcion = ""
    while opcion != opcion_volver:
        menu_nivel_socio()
        opcion = input("\nsubmenu@> ").strip()

        if opcion in [str(i) for i in range(1, len(NIVELES_SOCIO) + 1)]:
            consulta_por_nivel_socioeconomico(G, NIVELES_SOCIO[int(opcion) - 1][0])
        elif opcion == opcion_todos:
            consulta_todos_los_niveles(G)
        elif opcion == opcion_volver:
            print("Regresando al menú principal...")
        else:
            print("Opcion no valida. Vuelve a intentarlo")


def demo_nivel_socioeconomico(G):
    """Demo completa: resumen, detalle por nivel y gráfica de barras."""
    datos = obtener_niveles_socio(G)
    if not datos:
        print(f"\n[!] No se encontró el bloque '{NOMBRE_BLOQUE_SOCIO}' en el grafo.")
        return

    print("\n" + "=" * 65)
    print(" DEMO: CONSULTA POR NIVEL SOCIOECONÓMICO")
    print(f" Bloque consultado: {NOMBRE_BLOQUE_SOCIO}")
    print("=" * 65)

    # 1. Resumen: cuántos alumnos hay en cada nivel
    print("\nCriterio de clasificación:")
    for nombre, mn, mx in NIVELES_SOCIO:
        total = sum(1 for r in datos if r[2] == nombre)
        print(f"  • {nombre:<6} ({mn}-{mx}) -> {total} alumno(s)")

    # 2. Detalle por nivel (de Alto a Bajo)
    for nombre, _, _ in reversed(NIVELES_SOCIO):
        consulta_por_nivel_socioeconomico(G, nombre)

    # 3. Gráfica de barras con colores por nivel
    etiquetas = [f"{a}\n{nombre_nodo(G, a)}" for a, _, _ in datos]
    puntajes = [p for _, p, _ in datos]
    colores = [COLORES_NIVEL[n] for _, _, n in datos]

    plt.figure(figsize=(10, 6))
    barras = plt.bar(etiquetas, puntajes, color=colores, edgecolor="black")
    for barra, p in zip(barras, puntajes):
        plt.text(barra.get_x() + barra.get_width() / 2, p + 0.8, str(p), ha="center", fontweight="bold")

    # Líneas de corte entre niveles
    plt.axhline(NIVELES_SOCIO[1][1] - 0.5, color="gray", linestyle="--", linewidth=1)
    plt.axhline(NIVELES_SOCIO[2][1] - 0.5, color="gray", linestyle="--", linewidth=1)

    leyenda = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORES_NIVEL.values()]
    plt.legend(leyenda, [f"{n} ({mn}-{mx})" for n, mn, mx in NIVELES_SOCIO], title="Nivel")
    plt.ylim(0, 110)
    plt.ylabel("Puntaje")
    plt.title("Nivel socioeconómico por alumno", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()
