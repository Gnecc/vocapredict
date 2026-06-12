#!/usr/bin/env python3
"""Expand the socioeconomic survey with traceable categorical synthetic rows."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ORIGIN_COLUMN = "origen_registro"
REAL_LABEL = "real"
SYNTHETIC_LABEL = "sintetico"


def load_real_rows(path: Path) -> pd.DataFrame:
    dataset = pd.read_csv(path, dtype=str, keep_default_na=False)
    if ORIGIN_COLUMN in dataset.columns:
        dataset = dataset[dataset[ORIGIN_COLUMN] == REAL_LABEL].drop(
            columns=[ORIGIN_COLUMN]
        )
    return dataset.reset_index(drop=True)


def row_distances(features: pd.DataFrame, seed_index: int) -> np.ndarray:
    comparable = features.drop(columns=[features.columns[0]])
    seed = comparable.iloc[seed_index]
    distances = (comparable != seed).mean(axis=1).to_numpy(dtype=float)
    distances[seed_index] = np.inf
    return distances


def generate_synthetic_rows(
    real: pd.DataFrame,
    count: int,
    random_seed: int,
    neighbor_pool: int,
) -> pd.DataFrame:
    if count <= 0:
        return pd.DataFrame(columns=real.columns)

    rng = np.random.default_rng(random_seed)
    feature_columns = list(real.columns)
    identifier_column = feature_columns[0]
    blocks = [
        feature_columns[1:3],   # Age and current education level
        feature_columns[3:15],  # Income, household education/assets and size
        feature_columns[15:22], # Food consumption
    ]

    existing_signatures = {
        tuple(row)
        for row in real[feature_columns[1:]].itertuples(index=False, name=None)
    }
    synthetic_rows: list[dict[str, str]] = []
    attempts = 0
    max_attempts = count * 500

    while len(synthetic_rows) < count and attempts < max_attempts:
        attempts += 1
        seed_index = int(rng.integers(0, len(real)))
        distances = row_distances(real, seed_index)
        candidates = np.argsort(distances)[: min(neighbor_pool, len(real) - 1)]

        row = real.iloc[seed_index].copy()
        replace_count = int(rng.integers(1, len(blocks)))
        selected_blocks = rng.choice(
            len(blocks),
            size=replace_count,
            replace=False,
        )

        for block_index in selected_blocks:
            donor_index = int(rng.choice(candidates))
            block = blocks[int(block_index)]
            row.loc[block] = real.loc[donor_index, block]

        signature = tuple(row[column] for column in feature_columns[1:])
        if signature in existing_signatures:
            continue

        row[identifier_column] = f"SINT-{len(synthetic_rows) + 1:04d}"
        existing_signatures.add(signature)
        synthetic_rows.append(row.to_dict())

    if len(synthetic_rows) != count:
        raise RuntimeError(
            f"Only {len(synthetic_rows)} unique rows could be generated "
            f"after {attempts} attempts."
        )

    return pd.DataFrame(synthetic_rows, columns=feature_columns)


def augment(
    input_path: Path,
    output_path: Path,
    target_rows: int,
    random_seed: int,
    neighbor_pool: int,
) -> None:
    real = load_real_rows(input_path)
    if len(real) > target_rows:
        raise ValueError(
            f"The dataset already has {len(real)} real rows, above target "
            f"{target_rows}."
        )

    synthetic = generate_synthetic_rows(
        real=real,
        count=target_rows - len(real),
        random_seed=random_seed,
        neighbor_pool=neighbor_pool,
    )

    real[ORIGIN_COLUMN] = REAL_LABEL
    synthetic[ORIGIN_COLUMN] = SYNTHETIC_LABEL
    augmented = pd.concat([real, synthetic], ignore_index=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    augmented.to_csv(output_path, index=False)
    print(
        f"Created {output_path} with {len(real)} real rows and "
        f"{len(synthetic)} synthetic rows ({len(augmented)} total)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand the socioeconomic survey to a target row count."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-rows", type=int, default=351)
    parser.add_argument("--random-seed", type=int, default=20260612)
    parser.add_argument("--neighbor-pool", type=int, default=15)
    args = parser.parse_args()

    augment(
        input_path=args.input,
        output_path=args.output,
        target_rows=args.target_rows,
        random_seed=args.random_seed,
        neighbor_pool=args.neighbor_pool,
    )


if __name__ == "__main__":
    main()
