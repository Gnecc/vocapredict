"""Búsqueda de alumnos por número de control o por nombre."""
from visualizacion import graficar_subgrafo_alumno


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
