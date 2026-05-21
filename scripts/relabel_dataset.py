#!/usr/bin/env python3
"""Relabel vocational preference datasets against target career profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = [
    "calculo",
    "c. fisico",
    "c. biologico",
    "mecanico",
    "servicio social",
    "literario",
    "persuasivo",
    "artistico",
    "musical",
]

# Target profiles agreed from the career reading:
# - ICO: technical computing / hardware orientation.
# - ISC: engineering systems and communications orientation.
# - LIA: technology applied to administration and organizations.
# - LLE: languages, communication, and humanistic orientation.
TARGET_PROFILES = {
    "ICO": [0.90, 0.80, 0.25, 0.90, 0.35, 0.35, 0.45, 0.30, 0.25],
    "ISC": [0.90, 0.90, 0.25, 0.70, 0.50, 0.45, 0.55, 0.35, 0.25],
    "LIA": [0.65, 0.35, 0.25, 0.35, 0.75, 0.55, 0.90, 0.45, 0.30],
    "LLE": [0.25, 0.25, 0.25, 0.25, 0.75, 0.95, 0.75, 0.65, 0.40],
}


def normalized_feature_names(columns: list[str]) -> list[str]:
    replacements = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "A",
            "É": "E",
            "Í": "I",
            "Ó": "O",
            "Ú": "U",
        }
    )
    return [str(column).strip().translate(replacements).lower() for column in columns]


def load_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def score_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_features = list(df.columns[:-1])
    label_column = df.columns[-1]
    normalized = normalized_feature_names(source_features)

    if normalized != FEATURES:
        raise ValueError(
            "Unexpected feature columns. "
            f"Expected {FEATURES}, received {normalized}."
        )

    values = df[source_features].to_numpy(dtype=float)
    profile_labels = list(TARGET_PROFILES)
    profiles = np.array([TARGET_PROFILES[label] for label in profile_labels], dtype=float)

    distances = np.linalg.norm(values[:, None, :] - profiles[None, :, :], axis=2)
    ranked = np.argsort(distances, axis=1)
    best_idx = ranked[:, 0]
    second_idx = ranked[:, 1]
    new_labels = np.array(profile_labels, dtype=object)[best_idx]
    old_labels = df[label_column].astype(str).str.strip().to_numpy()

    relabeled = df.copy()
    relabeled[label_column] = new_labels

    audit = pd.DataFrame(
        {
            "row_excel_1based": np.arange(len(df)) + 2,
            "old_label": old_labels,
            "new_label": new_labels,
            "changed": old_labels != new_labels,
            "best_distance": distances[np.arange(len(df)), best_idx],
            "second_label": np.array(profile_labels, dtype=object)[second_idx],
            "second_distance": distances[np.arange(len(df)), second_idx],
        }
    )
    audit["margin"] = audit["second_distance"] - audit["best_distance"]

    for index, label in enumerate(profile_labels):
        audit[f"distance_{label}"] = distances[:, index]

    return relabeled, audit


def write_outputs(
    input_path: Path,
    csv_output: Path | None,
    audit_output: Path | None,
    summary_output: Path | None,
) -> dict:
    dataset = load_dataset(input_path)
    relabeled, audit = score_rows(dataset)
    label_column = dataset.columns[-1]

    summary = {
        "input": str(input_path),
        "rows": int(len(dataset)),
        "label_column": str(label_column),
        "old_counts": dataset[label_column].astype(str).str.strip().value_counts().to_dict(),
        "new_counts": relabeled[label_column].value_counts().to_dict(),
        "changed_rows": int(audit["changed"].sum()),
        "transition_counts": {
            f"{old}->{new}": int(count)
            for (old, new), count in audit[audit["changed"]]
            .groupby(["old_label", "new_label"])
            .size()
            .items()
        },
        "profiles": TARGET_PROFILES,
    }

    if csv_output is not None:
        csv_output.parent.mkdir(parents=True, exist_ok=True)
        relabeled.to_csv(csv_output, index=False)

    if audit_output is not None:
        audit_output.parent.mkdir(parents=True, exist_ok=True)
        audit.round(6).to_csv(audit_output, index=False)

    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(
            json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Relabel a vocational preferences dataset from target profiles."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path)
    parser.add_argument("--audit-output", type=Path)
    parser.add_argument("--summary-output", type=Path)
    args = parser.parse_args()

    summary = write_outputs(
        input_path=args.input,
        csv_output=args.csv_output,
        audit_output=args.audit_output,
        summary_output=args.summary_output,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
