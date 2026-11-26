"""Genera las referencias del catálogo y compara su cobertura histórica."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.riasec import BACKEND_DIR, DATASET, FEATURES
from red_semantica.riasec_owl import (
    AREAS, REFERENCIAS_CSV, cargar_catalogo, inferir, intereses_destacados, validar_puntajes,
)
from scripts.compare_riasec_43 import comparison_split_43


def codigo_referencia(puntajes):
    medias = puntajes.loc[:, FEATURES].mean().to_numpy()
    return "".join(AREAS[i] for i in np.argsort(-medias, kind="stable")[:3])


def generar_referencias(catalogo, entrenamiento):
    referencias = {}
    for opcion in catalogo["opciones"]:
        codigo = opcion["id"]
        if "referencia" in opcion or codigo == "CPE":
            continue
        filas = entrenamiento.loc[entrenamiento.career_code.eq(codigo)]
        if filas.empty:
            raise ValueError(f"No hay perfiles de entrenamiento para {codigo}.")
        referencias[codigo] = {
            "programa": opcion["nombre"],
            "codigo": codigo_referencia(filas),
            "fuente": "https://openpsychometrics.org/_rawdata/",
            "perfiles_entrenamiento": len(filas),
        }
    return referencias


def evaluar(catalogo, prueba, cpe_experimental=None):
    codigos = {o["id"]: o["referencia"]["codigo"] for o in catalogo["opciones"] if "referencia" in o}
    if cpe_experimental:
        codigos["CPE"] = cpe_experimental
    resultados_por_patron = {}
    conteos = []
    coincidencias = []
    for fila in prueba.loc[:, [*FEATURES, "career_code"]].itertuples(index=False, name=None):
        *valores, carrera = fila
        patron = frozenset(intereses_destacados(validar_puntajes(valores)))
        if patron not in resultados_por_patron:
            opciones = {codigo for codigo, letras in codigos.items() if len(patron.intersection(letras)) >= 2}
            _, resultados = inferir(catalogo, valores, cpe_experimental)
            if opciones != {opcion["id"] for opcion, _ in resultados}:
                raise RuntimeError(f"La evaluación no coincide con OWL-RL para el patrón {sorted(patron)}.")
            resultados_por_patron[patron] = opciones
        opciones = resultados_por_patron[patron]
        conteos.append(len(opciones))
        coincidencias.append(("CPE" if carrera in {"COM", "JOU"} else carrera) in opciones)
    return pd.DataFrame({"conexiones": conteos, "coincide": coincidencias}, index=prueba.index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()
    _, entrenamiento, compartidos, nuevos = comparison_split_43(args.baseline, args.dataset)
    prueba = pd.concat((compartidos, nuevos), verify_integrity=True)
    original = cargar_catalogo()
    referencias = generar_referencias(original, entrenamiento)
    if len(referencias) != 28:
        raise ValueError(f"Se esperaban 28 referencias nuevas; se obtuvieron {len(referencias)}.")
    ampliado = {**original, "opciones": [
        {**opcion, "referencia": referencias[opcion["id"]]}
        if opcion["id"] in referencias else opcion for opcion in original["opciones"]
    ]}
    control = evaluar(original, prueba)
    ensayo = evaluar(ampliado, prueba, "AEI")

    lines = [
        "# Referencias ampliadas de la ontología RIASEC", "",
        f"Se generaron 28 referencias con los {len(entrenamiento):,} perfiles de entrenamiento",
        "de la partición de 43 carreras. Cada código ordena las tres áreas con mayor puntaje",
        "promedio en los perfiles que declararon esa carrera. Los empates se ordenan por R I A S E C.",
        "Las 13 referencias de Zenodo se conservan y Comunicación y Periodismo usa AEI experimental.",
        f"La misma prueba de {len(prueba):,} perfiles se usa en ambas variantes.",
        "Se comprobó que los resultados por patrón de intereses coinciden con OWL-RL.",
        "La web sigue usando el catálogo habitual.", "",
        "| Catálogo | Perfiles con conexión | Conexiones totales | Promedio | Mediana | Máximo | Carrera declarada incluida* |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for nombre, resultados in (("13 referencias", control), ("42 referencias", ensayo)):
        c = resultados.conexiones
        lines.append(f"| {nombre} | {(c > 0).sum():,} ({(c > 0).mean():.1%}) | {c.sum():,} | "
                     f"{c.mean():.2f} | {c.median():g} | {c.max()} | {resultados.coincide.sum():,} ({resultados.coincide.mean():.1%}) |")
    lines += ["", "* Comunicación y Periodismo se consideran una opción compartida. La proporción",
              "indica presencia de la carrera declarada entre todas las conexiones. Una lista más",
              "larga puede aumentarla sin que mejore la capacidad de distinguir carreras.", "",
              f"Perfiles con más de diez conexiones en el catálogo ampliado: "
              f"{(ensayo.conexiones > 10).sum():,} ({(ensayo.conexiones > 10).mean():.1%}).", "",
              "## Comunicación y Periodismo", ""]
    for codigo, nombre in (("COM", "Comunicación"), ("JOU", "Periodismo")):
        casos = prueba.career_code.eq(codigo)
        lines.append(f"- {nombre}: AEI conecta con {ensayo.loc[casos, 'coincide'].sum()} de {casos.sum()} perfiles.")
    lines += ["", "## Referencias derivadas del CSV", "",
              "El código de prueba se calcula aparte para comprobar si contiene las mismas áreas.",
              "La referencia publicada se calcula solo con entrenamiento.", "",
              "| Carrera | Código de entrenamiento | Perfiles de entrenamiento | Código de prueba |",
              "|---|---|---:|---|"]
    for codigo, ref in referencias.items():
        comparacion = codigo_referencia(prueba.loc[prueba.career_code.eq(codigo)])
        lines.append(f"| {ref['programa']} | {ref['codigo']} | {ref['perfiles_entrenamiento']:,} | {comparacion} |")

    REFERENCIAS_CSV.write_text(json.dumps(referencias, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = BACKEND_DIR / "docs" / "referencias_ampliadas_riasec.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
