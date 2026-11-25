"""Reportes impresos en consola."""
from utils import formato_relacion


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

    for origen, destino, relacion, props in relaciones_instancias[:25]:
        nombre_origen = dict_nombres.get(origen, origen)
        nombre_destino = dict_nombres.get(destino, destino)
        print(f"{nombre_origen:<20} -- {formato_relacion(relacion, props)} --> {nombre_destino}")

    print("\n" + "=" * 60)
