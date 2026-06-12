#!/usr/bin/env python3
"""Apply the AMAI 2024 socioeconomic classification to the survey dataset."""

from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import pandas as pd


EDUCATION_COLUMN = (
    "Pensando en el jefe o jefa del hogar , ¿cuál fue el último grado de "
    "estudios que aprobó en la escuela?"
)
BATHROOMS_COLUMN = (
    "¿Cuántos baños completos tiene esta vivienda con excusado/WC y regadera?"
)
CARS_COLUMN = (
    "¿Cuántos automóviles, camionetas cerradas, vans o pick-ups tiene este hogar?"
)
INTERNET_COLUMN = (
    "Sin tomar en cuenta la conexión móvil desde algún celular, "
    "¿su hogar cuenta con internet?"
)
WORKERS_COLUMN = (
    "¿Cuántas personas de 14 años o más trabajan actualmente o trabajaron "
    "el mes pasado?"
)
BEDROOMS_COLUMN = "¿Cuántos cuartos tiene su casa que se utilizan para dormir?"

AMAI_MAX_SCORE = 300

EDUCATION_POINTS = {
    "sin instruccion": 0,
    "no estudio": 0,
    "primaria incompleta": 6,
    "primaria completa": 11,
    "secundaria incompleta": 12,
    "secundaria completa": 18,
    "carrera comercial": 23,
    "carrera tecnica": 23,
    "preparatoria incompleta": 23,
    "preparatoria completa": 27,
    "licenciatura incompleta": 36,
    "licenciatura completa": 59,
    "diplomado o maestria": 85,
    "doctorado": 85,
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).strip().lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def parse_count(value: str) -> int:
    normalized = normalize_text(value)
    if normalized in {"mas de 3", "más de 3"}:
        return 4
    return int(float(normalized))


def education_score(value: str) -> int:
    key = normalize_text(value)
    if key not in EDUCATION_POINTS:
        raise ValueError(f"Unsupported AMAI education category: {value!r}")
    return EDUCATION_POINTS[key]


def bathroom_score(value: str) -> int:
    count = parse_count(value)
    return 0 if count == 0 else 24 if count == 1 else 47


def car_score(value: str) -> int:
    count = parse_count(value)
    return 0 if count == 0 else 22 if count == 1 else 43


def internet_score(value: str) -> int:
    answer = normalize_text(value)
    if answer == "si":
        return 32
    if answer == "no":
        return 0
    raise ValueError(f"Unsupported AMAI internet category: {value!r}")


def worker_score(value: str) -> int:
    count = parse_count(value)
    return {0: 0, 1: 15, 2: 31, 3: 46}.get(count, 61)


def bedroom_score(value: str) -> int:
    count = parse_count(value)
    return {0: 0, 1: 8, 2: 16, 3: 24}.get(count, 32)


def classify(score: int) -> str:
    if score >= 202:
        return "A/B"
    if score >= 168:
        return "C+"
    if score >= 141:
        return "C"
    if score >= 116:
        return "C-"
    if score >= 95:
        return "D+"
    if score >= 48:
        return "D"
    return "E"


def apply_amai(input_path: Path, output_path: Path) -> None:
    dataset = pd.read_csv(input_path, dtype=str, keep_default_na=False)

    scores = (
        dataset[EDUCATION_COLUMN].map(education_score)
        + dataset[BATHROOMS_COLUMN].map(bathroom_score)
        + dataset[CARS_COLUMN].map(car_score)
        + dataset[INTERNET_COLUMN].map(internet_score)
        + dataset[WORKERS_COLUMN].map(worker_score)
        + dataset[BEDROOMS_COLUMN].map(bedroom_score)
    )

    dataset["nivel_socioeconomico_amai"] = scores.map(classify)
    dataset["valor_amai_normalizado"] = (scores / AMAI_MAX_SCORE).round(6)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    print(f"Created {output_path} with {len(dataset)} AMAI-classified rows.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply AMAI 2024 classification.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    apply_amai(args.input, args.output)


if __name__ == "__main__":
    main()
