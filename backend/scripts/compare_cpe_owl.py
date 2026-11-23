"""Compare CPE reference codes on the historical RIASEC split."""

import argparse
from pathlib import Path

import pandas as pd

from models.riasec import BACKEND_DIR, DATASET, FEATURES
from red_semantica.riasec_owl import CPE_EXPERIMENTOS, intereses_destacados, validar_puntajes
from scripts.compare_riasec import percent
from scripts.compare_riasec_43 import comparison_split_43


def evaluar(rows, codigos):
    areas = [
        intereses_destacados(validar_puntajes(puntajes))
        for puntajes in rows.loc[:, FEATURES].itertuples(index=False, name=None)
    ]
    resultados = {}
    for codigo in codigos:
        letras = set(codigo)
        conecta = pd.Series([len(letras & perfil) >= 2 for perfil in areas], index=rows.index)
        com = rows.career_code.eq("COM")
        jou = rows.career_code.eq("JOU")
        positivos = com | jou
        com_ok = int((conecta & com).sum())
        jou_ok = int((conecta & jou).sum())
        aciertos = com_ok + jou_ok
        conexiones = int(conecta.sum())
        resultados[codigo] = {
            "conexiones": conexiones, "aciertos": aciertos,
            "precision": aciertos / conexiones if conexiones else 0,
            "recobrado": aciertos / int(positivos.sum()),
            "f1": 2 * aciertos / (conexiones + int(positivos.sum())),
            "com": f"{com_ok}/{int(com.sum())}",
            "jou": f"{jou_ok}/{int(jou.sum())}",
            "otras": f"{conexiones - aciertos}/{int((~positivos).sum())}",
        }
    return resultados


def tabla(resultados):
    lines = [
        "| Código | Conexiones | Comunicación | Periodismo | Otras carreras | Precisión | Recobrado | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for codigo, m in resultados.items():
        lines.append(
            f"| {codigo} | {m['conexiones']:,} | {m['com']} | {m['jou']} | {m['otras']} | "
            f"{percent(m['precision'])} | {percent(m['recobrado'])} | {percent(m['f1'])} |"
        )
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()
    _, train43, shared, new = comparison_split_43(args.baseline, args.dataset)
    train_metrics = evaluar(train43, CPE_EXPERIMENTOS)
    variante = max(CPE_EXPERIMENTOS[1:], key=lambda c: train_metrics[c]["f1"])
    test = pd.concat([shared, new], verify_integrity=True)
    test_metrics = evaluar(test, ("AES", variante))
    lines = [
        "# Comunicación y Periodismo con Investigación en la ontología RIASEC", "",
        "Se compara AES, código de Zenodo, con tres variantes que sustituyen una letra",
        "por I (Investigador). Las variantes son hipótesis del proyecto basadas en",
        "las asignaturas de métodos y reportaje de FES Aragón. El orden de las letras",
        "se conserva para lectura. La regla actual usa el conjunto de letras.", "",
        "[Catálogo Zenodo](https://doi.org/10.5281/zenodo.21403867) · "
        "[Plan de FES Aragón](https://www.aragon.unam.mx/fes-aragon/public_html/documents/licenciaturas/comunicacion-y-periodismo/plan-de-estudios-comunicacion-y-periodismo.pdf)",
        "", f"Se elige la variante por F1 en los {len(train43):,} casos de entrenamiento.",
        f"La comparación final usa los {len(test):,} perfiles de prueba previos,",
        "incluidos 219 con Comunicación y 72 con Periodismo declarado. Las demás carreras",
        "sirven para medir cuántas veces se muestra la conexión fuera del grupo. Esto evalúa",
        "coincidencia con una carrera declarada en una muestra internacional. La partición",
        "ya se usó en experimentos previos.", "",
        "La comparación masiva aplica el mismo criterio de la consulta OWL. Usa las áreas",
        "por encima del cuarto lugar y exige dos coincidencias. La prueba individual",
        "comprueba que OWL-RL deduzca la candidatura y que se devuelva la evidencia.", "",
        "## Selección en entrenamiento", "", *tabla(train_metrics),
        "", f"Variante elegida **{variante}**.", "",
        "## Comparación en prueba", "", *tabla(test_metrics), "",
        "Desde `backend/`, con el CSV histórico de 40 carreras:", "",
        "```bash",
        "python3 -m scripts.compare_cpe_owl --baseline /ruta/al/csv-historico.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "comunicacion_periodismo_owl.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
