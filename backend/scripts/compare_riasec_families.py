"""Compare flat and hierarchical RIASEC prediction with country holdouts."""

import argparse
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from models.riasec import BACKEND_DIR, FEATURES
from scripts.benchmark_riasec_40 import respuestas_originales
from scripts.compare_riasec import load_profiles, percent, split, train


# Exploratory families defined by discipline before evaluating the models.
FAMILIES = {
    "Administración y economía": "ACC BAM ECO FIN MKT",
    "Arte y diseño": "ARC GDE MUS",
    "Ciencias naturales y matemáticas": "BCH BIO CHE MAT PHY",
    "Ciencias sociales": "ANT GEO IRL POL SOC SWK",
    "Computación y software": "CENM CENR CSC",
    "Derecho y justicia": "CRI CRJ LAW",
    "Educación": "EDU",
    "Humanidades y comunicación": "HIS JOU LIN PHI",
    "Ingeniería": "CEN CIV ELE IND MEC",
    "Salud y comportamiento": "KIN MED NUR PHA PSY",
}
FAMILY_BY_CODE = {code: family for family, codes in FAMILIES.items() for code in codes.split()}


def fit_logistic(x, y):
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=600)).fit(x, y)


def classify_family_probabilities(career_scores, careers, families):
    """Add scores for careers in the same family."""
    memberships = np.array([FAMILY_BY_CODE[career] for career in careers])
    return np.column_stack([
        career_scores[:, memberships == family].sum(axis=1) for family in families
    ])


def measure(scores, classes, actual):
    ranked = classes[np.argsort(-scores, axis=1, kind="stable")[:, :3]]
    top1 = ranked[:, 0] == actual
    top3 = (ranked == actual[:, None]).any(axis=1)
    recalls = [top1[actual == code].mean() for code in np.unique(actual)]
    return top1.mean(), top3.mean(), np.mean(recalls), ranked


def most_frequent(classes, labels, rows):
    counts = Counter(labels)
    return np.tile([counts[label] for label in classes], (rows, 1))


def selective_prediction(training, test, items):
    fit, validation = split(training)
    model = fit_logistic(items.loc[fit.index], fit.career_code)
    probabilities = model.predict_proba(items.loc[validation.index])
    correct = model.classes_[probabilities.argmax(axis=1)] == validation.career_code.to_numpy()
    confidence = probabilities.max(axis=1)
    # Choose the first threshold that reaches the goal with enough validation cases.
    for threshold in (step / 100 for step in range(35, 96)):
        chosen = confidence >= threshold
        if chosen.sum() >= 100 and correct[chosen].mean() >= 0.8:
            probabilities = model.predict_proba(items.loc[test.index])
            selected = probabilities.max(axis=1) >= threshold
            predicted = model.classes_[probabilities.argmax(axis=1)]
            hits = (predicted == test.career_code.to_numpy()) & selected
            return threshold, int(chosen.sum()), correct[chosen].mean(), int(hits.sum()), Counter(predicted[selected])
    return None


def run_split(training, test, items):
    x_train, x_test = items.loc[training.index], items.loc[test.index]
    train_careers, true_careers = training.career_code.to_numpy(), test.career_code.to_numpy()
    train_families = training.career_code.map(FAMILY_BY_CODE).to_numpy()
    true_families = test.career_code.map(FAMILY_BY_CODE).to_numpy()
    family = fit_logistic(x_train, train_families)
    flat = fit_logistic(x_train, train_careers)
    classic = train(training)
    careers = flat.classes_
    flat_scores = flat.predict_proba(x_test)
    family_scores = family.predict_proba(x_test)
    hierarchy = np.zeros_like(flat_scores)
    positions = {code: idx for idx, code in enumerate(careers)}
    for idx, name in enumerate(family.classes_):
        members = train_families == name
        codes = np.unique(train_careers[members])
        if len(codes) > 1:
            local = fit_logistic(x_train.loc[members], train_careers[members])
            codes = local.classes_
            conditional = local.predict_proba(x_test)
        else:
            conditional = 1.0
        columns = [positions[code] for code in codes]
        hierarchy[:, columns] = family_scores[:, idx, None] * conditional

    # The grouped prediction and individual-career prediction are distinct tasks.
    career_results = {
        "Por frecuencia": measure(most_frequent(careers, train_careers, len(test)), careers, true_careers),
        "Logística ponderada · 6 puntajes": measure(
            classic.predict_proba(test.loc[:, FEATURES].to_numpy()), classic.classes_, true_careers,
        ),
        "Logística directa · 48 respuestas": measure(flat_scores, careers, true_careers),
        "Logística jerárquica · 48 respuestas": measure(hierarchy, careers, true_careers),
    }
    family_results = {
        "Por frecuencia": measure(
            most_frequent(family.classes_, train_families, len(test)), family.classes_, true_families,
        ),
        "Agrupando puntajes del modelo de carreras": measure(
            classify_family_probabilities(flat_scores, careers, family.classes_),
            family.classes_, true_families,
        ),
        "Modelo directo de familias · 48 respuestas": measure(family_scores, family.classes_, true_families),
    }
    return career_results, family_results, true_families


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--raw-riasec", type=Path, required=True)
    args = parser.parse_args()
    rows = load_profiles(args.baseline)
    careers = set(rows.career_code)
    if len(careers) != 40 or careers != FAMILY_BY_CODE.keys() or sum(
        len(codes.split()) for codes in FAMILIES.values()
    ) != 40:
        raise ValueError("El mapa debe cubrir exactamente las 40 carreras elegibles.")
    items = respuestas_originales(args.raw_riasec, rows)
    historical = split(rows)
    lines = [
        "# RIASEC: familias vocacionales y transferencia entre países", "",
        "Se compara la predicción de 40 carreras con dos estrategias de agrupación.",
        "Una suma los puntajes de carreras por familia y la otra aprende las familias",
        "directamente. La variante jerárquica multiplica el puntaje de cada familia",
        "por la probabilidad de la carrera dentro de ella, sin descartar familias.",
        "Las agrupaciones se definieron por disciplina antes de la prueba.",
        "La etiqueta sigue siendo la carrera o familia declarada, medida en tareas distintas.",
        "La referencia por frecuencia usa las clases más frecuentes del entrenamiento.", "",
        "La prueba histórica se ha usado antes. En las pruebas por país se excluye del",
        "entrenamiento cada fila con el código evaluado. Esos códigos reflejan ubicación",
        "de conexión. La evaluación MX es exploratoria por su tamaño y procedencia.",
        "Estos ejercicios reutilizan la colección original y no sustituyen una prueba prospectiva.",
        "", "## Familias", "",
        "| Familia | Carreras |", "|---|---|",
    ]
    names = rows.set_index("career_code")["career_name"].to_dict()
    for family, codes in FAMILIES.items():
        lines.append(f"| {family} | {', '.join(names[code] for code in codes.split())} |")
    lines += ["", "## Resultados", "",
              "| Partición | Casos | Objetivo | Modelo | Top 1 | Top 3 | Exactitud equilibrada |",
              "|---|---:|---|---|---:|---:|---:|"]
    confusion_sections = []
    selective_lines = [
        "", "## Primera opción con abstención", "",
        "Se ajusta una logística directa con 48 respuestas. En una partición interna",
        "se elige el umbral de menor valor, en pasos de 0.01 de 0.35 a 0.95, que alcance",
        "80 % de aciertos en al menos 100 casos aceptados. En prueba el modelo solo",
        "reporta una carrera si su puntuación máxima supera o iguala ese umbral.",
        "Se muestran tanto la exactitud de las respuestas emitidas como su cobertura.", "",
        "| Partición | Umbral | Aceptados en validación | Exactitud validación | Aciertos / sugerencias | Exactitud prueba | Cobertura prueba | Sugerencia más frecuente |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    detail = []
    for name, (training, test) in (
        ("Histórica", historical),
        ("País fuera · US", (rows.loc[~rows.country.eq("US")], rows.loc[rows.country.eq("US")])),
        ("País fuera · MX", (rows.loc[~rows.country.eq("MX")], rows.loc[rows.country.eq("MX")])),
    ):
        if set(training.index) & set(test.index) or set(training.career_code) != careers:
            raise ValueError(f"Partición inválida: {name}")
        career_results, family_results, true_families = run_split(training, test, items)
        for target, results in (("Carrera", career_results), ("Familia", family_results)):
            for model, (top1, top3, balanced, _) in results.items():
                lines.append(f"| {name} | {len(test):,} | {target} | {model} | {percent(top1)} | "
                             f"{percent(top3)} | {percent(balanced)} |")

        selected = selective_prediction(training, test, items)
        if selected is None:
            selective_lines.append(f"| {name} | Sin umbral | — | — | — | — | — | — |")
        else:
            threshold, val_count, val_accuracy, hits, suggestions = selected
            offered = sum(suggestions.values())
            accuracy = percent(hits / offered) if offered else "—"
            most_common = "—"
            if suggestions:
                code, frequency = suggestions.most_common(1)[0]
                most_common = f"{names[code]} ({frequency}/{offered})"
            selective_lines.append(
                f"| {name} | {threshold:.2f} | {val_count} | {percent(val_accuracy)} | "
                f"{hits}/{offered} | {accuracy} | {percent(offered / len(test))} | {most_common} |"
            )

        if name == "Histórica":
            family_ranks = family_results["Agrupando puntajes del modelo de carreras"][3]
            detail = [
                "", "## Aciertos por familia en la prueba histórica", "",
                "| Familia | Casos | Top 1 | Top 3 |", "|---|---:|---:|---:|",
            ]
            for family in FAMILIES:
                matches = family_ranks[true_families == family] == family
                detail.append(f"| {family} | {len(matches):,} | {percent(matches[:, 0].mean())} | "
                              f"{percent(matches.any(axis=1).mean())} |")
            predicted = career_results["Logística directa · 48 respuestas"][3][:, 0]
            true = test.career_code.to_numpy()
            confusion = Counter((a, b) for a, b in zip(true, predicted) if a != b)
            confusion_sections += [
                "", "## Confusiones en la prueba histórica", "",
                f"Las confusiones entre carreras de una misma familia suman "
                f"{sum(n for (a, b), n in confusion.items() if FAMILY_BY_CODE[a] == FAMILY_BY_CODE[b]):,}"
                f" de {sum(confusion.values()):,} errores en primera opción de la logística directa.",
                "", "| Carrera declarada | Primera opción errónea | Casos |", "|---|---|---:|",
            ]
            for (a, b), n in confusion.most_common(12):
                confusion_sections.append(f"| {names[a]} | {names[b]} | {n} |")
        print(f"{name}: {len(training):,} entrenamiento, {len(test):,} prueba", flush=True)
    lines += detail + selective_lines + confusion_sections + [
        "", "Desde `backend/`:", "", "```bash",
        "python3 -m scripts.compare_riasec_families --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "familias_riasec_40.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
