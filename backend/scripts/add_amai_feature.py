#!/usr/bin/env python3
"""Add the row-aligned normalized AMAI value to the augmented ML dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


AMAI_COLUMN = "valor_amai_normalizado"
TARGET_COLUMN = "CARRERA_ACTUAL"


def add_amai_feature(
    dataset_path: Path,
    socioeconomic_path: Path,
    output_path: Path,
) -> None:
    dataset = pd.read_csv(dataset_path)
    socioeconomic = pd.read_csv(socioeconomic_path)

    if len(dataset) != len(socioeconomic):
        raise ValueError(
            "The files must have the same number of rows: "
            f"{len(dataset)} != {len(socioeconomic)}."
        )
    if AMAI_COLUMN not in socioeconomic.columns:
        raise ValueError(f"Missing column {AMAI_COLUMN!r} in socioeconomic file.")
    if TARGET_COLUMN not in dataset.columns:
        raise ValueError(f"Missing target column {TARGET_COLUMN!r} in ML dataset.")

    if AMAI_COLUMN in dataset.columns:
        dataset = dataset.drop(columns=[AMAI_COLUMN])

    target_position = dataset.columns.get_loc(TARGET_COLUMN)
    dataset.insert(
        target_position,
        AMAI_COLUMN,
        socioeconomic[AMAI_COLUMN].to_numpy(),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    print(f"Created {output_path} with {len(dataset)} rows.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add normalized AMAI values to the augmented ML dataset."
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--socioeconomic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    add_amai_feature(
        dataset_path=args.dataset,
        socioeconomic_path=args.socioeconomic,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
