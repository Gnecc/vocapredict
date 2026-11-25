"""Punto de entrada: ejecuta el menú interactivo."""
import time
from ontologia import configurar_ontologia
from reportes import imprimir_reporte_ontologia
from visualizacion import visualizar_grafo
from busquedas import buscar, buscar_por_nombre
from consultas import consulta_por_enlace, consulta_por_propiedad, consulta_por_nodo
from nivel_socio import demo_nivel_socioeconomico, submenu_nivel_socioeconomico
from menu import menu


if __name__ == "__main__":
    G, alumnos, bloques, carreras, evaluaciones, relaciones = configurar_ontologia()
    rdf_perfiles = None
    op = "0"
    while op != "10":
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
                print("*" * 150, "\nCONSULTA POR ENLACE\n")
                consulta_por_enlace(G, input("Relación (evaluado / importante para / carrera sugerida): ").strip())

            case "6":
                print("*" * 150, "\nCONSULTA POR DATA PROPERTY (PUNTAJE)\n")
                try:
                    minimo = int(input("Puntaje mínimo: "))
                    maximo = int(input("Puntaje máximo: "))
                    consulta_por_propiedad(G, minimo, maximo)
                except ValueError:
                    print("[!] Ingresa números enteros.")

            case "7":
                print("*" * 150, "\nCONSULTA POR NODO AL QUE LLEVA\n")
                consulta_por_nodo(G, input("ID del nodo (ej. a1, b3, c1): ").strip())

            case "8":
                print("*" * 150, "\nDEMO: CONSULTA POR NIVEL SOCIOECONÓMICO\n")
                demo_nivel_socioeconomico(G)

            case "9":
                print("*" * 150, "\nSUBMENU: NIVEL SOCIOECONÓMICO\n")
                submenu_nivel_socioeconomico(G)

            case "11":
                from riasec_owl import cargar_catalogo, imprimir_inferencia, inferir

                catalogo = cargar_catalogo()
                valores = input("Seis puntajes en orden R I A S E C, separados por espacios: ").split()
                try:
                    _, resultados = inferir(catalogo, valores)
                    imprimir_inferencia(resultados, catalogo["fuente_referencias"])
                except ValueError as error:
                    print(f"[!] {error}")

            case "12":
                from riasec_owl import cargar_catalogo, imprimir_inferencia, inferir_perfil_csv

                perfil = input("Identificador de origen RIASEC (source_row_id): ").strip()
                try:
                    catalogo = cargar_catalogo()
                    _, resultados = inferir_perfil_csv(catalogo, perfil)
                    imprimir_inferencia(resultados, catalogo["fuente_referencias"])
                except (OSError, ValueError) as error:
                    print(f"[!] {error}")

            case "13":
                from inferencia import imprimir_afinidades
                imprimir_afinidades(G)

            case "14":
                fila_texto = input("Número de fila del CSV (o 'c' para cancelar): ").strip()
                if fila_texto.lower() == "c":
                    continue
                if not fila_texto.isdecimal() or int(fila_texto) < 1:
                    print("[!] Ingresa un número de fila positivo.")
                    continue
                from poblar_ontologia import cargar_csv_como_rdf, imprimir_inferencia_perfil
                try:
                    if rdf_perfiles is None:
                        print("Cargando perfiles del CSV y comprobando su procedencia...")
                        rdf_perfiles, origenes = cargar_csv_como_rdf()
                        print(f"Cargados {sum(origenes.values())} perfiles.")
                    imprimir_inferencia_perfil(rdf_perfiles, int(fila_texto))
                except (OSError, ValueError) as error:
                    print(f"[!] No se pudo consultar el perfil: {error}")

            case "10":
                print("Saliendo del sistema...")
                time.sleep(2.5)
                print("Adios...")
            case _:
                print("Opcion no valida. Vuelve a intentarlo")
                op = "0"
