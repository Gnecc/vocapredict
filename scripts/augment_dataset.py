#!/usr/bin/env python3
"""Create a balanced synthetic augmentation for the relabeled dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def nearest_neighbor_order(values: np.ndarray) -> np.ndarray:
    distances = np.linalg.norm(values[:, None, :] - values[None, :, :], axis=2)
    np.fill_diagonal(distances, np.inf)
    return np.argsort(distances, axis=1)


def synthesize_class(
    class_rows: pd.DataFrame,
    feature_columns: list[str],
    label_column: str,
    label: str,
    count: int,
    rng: np.random.Generator,
    k_neighbors: int,
) -> pd.DataFrame:
    if len(class_rows) < 2:
        raise ValueError(f"Class {label} needs at least two rows for interpolation.")

    values = class_rows[feature_columns].to_numpy(dtype=float)
    row_ids = class_rows.index.to_numpy()
    neighbor_order = nearest_neighbor_order(values)
    neighbor_limit = min(k_neighbors, len(class_rows) - 1)

    synthetic_rows = []
    for _ in range(count):
        seed_pos = int(rng.integers(0, len(class_rows)))
        neighbor_pos = int(rng.choice(neighbor_order[seed_pos, :neighbor_limit]))
        alpha = float(rng.random())
        synthetic_values = values[seed_pos] + alpha * (
            values[neighbor_pos] - values[seed_pos]
        )

        synthetic_row = dict(zip(feature_columns, synthetic_values))
        synthetic_row[label_column] = label
        synthetic_row["_origin"] = "synthetic"
        synthetic_row["_source_row_excel_1based"] = int(row_ids[seed_pos]) + 2
        synthetic_row["_neighbor_row_excel_1based"] = int(row_ids[neighbor_pos]) + 2
        synthetic_row["_alpha"] = alpha
        synthetic_rows.append(synthetic_row)

    return pd.DataFrame(synthetic_rows)


def augment_dataset(
    df: pd.DataFrame,
    target_per_class: int,
    random_seed: int,
    k_neighbors: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    feature_columns = list(df.columns[:-1])
    label_column = str(df.columns[-1])
    real = df.copy()
    real[label_column] = real[label_column].astype(str).str.strip()
    real["_origin"] = "real"
    real["_source_row_excel_1based"] = real.index.to_numpy() + 2
    real["_neighbor_row_excel_1based"] = np.nan
    real["_alpha"] = np.nan

    rng = np.random.default_rng(random_seed)
    synthetic_frames = []
    original_counts = real[label_column].value_counts().sort_index()

    for label, rows in real.groupby(label_column, sort=True):
        requested = target_per_class - len(rows)
        if requested < 0:
            raise ValueError(
                f"Class {label} already has {len(rows)} rows, above target "
                f"{target_per_class}."
            )
        if requested == 0:
            continue

        synthetic = synthesize_class(
            class_rows=rows,
            feature_columns=feature_columns,
            label_column=label_column,
            label=label,
            count=requested,
            rng=rng,
            k_neighbors=k_neighbors,
        )
        synthetic_frames.append(synthetic)

    synthetic_all = pd.concat(synthetic_frames, ignore_index=True)
    augmented_with_meta = pd.concat([real, synthetic_all], ignore_index=True)
    augmented_with_meta = augmented_with_meta.sample(
        frac=1,
        random_state=random_seed,
    ).reset_index(drop=True)

    audit = augmented_with_meta.rename(
        columns={
            "_origin": "origin",
            "_source_row_excel_1based": "source_row_excel_1based",
            "_neighbor_row_excel_1based": "neighbor_row_excel_1based",
            "_alpha": "alpha",
        }
    )
    audit.insert(0, "augmented_row_excel_1based", np.arange(len(audit)) + 2)
    audit.insert(len(feature_columns) + 1, "label", audit.pop(label_column))
    augmented = augmented_with_meta.drop(
        columns=[
            "_origin",
            "_source_row_excel_1based",
            "_neighbor_row_excel_1based",
            "_alpha",
        ]
    )

    augmented_counts = augmented[label_column].value_counts().sort_index()
    synthetic_count = int((audit["origin"] == "synthetic").sum())
    summary = {
        "rows_real": int(len(real)),
        "rows_synthetic": synthetic_count,
        "rows_augmented": int(len(augmented)),
        "synthetic_ratio": synthetic_count / len(augmented),
        "target_per_class": int(target_per_class),
        "random_seed": int(random_seed),
        "k_neighbors": int(k_neighbors),
        "label_column": label_column,
        "original_counts": original_counts.to_dict(),
        "augmented_counts": augmented_counts.to_dict(),
        "synthetic_needed_by_class": {
            label: int(target_per_class - count)
            for label, count in original_counts.items()
        },
    }
    return augmented, audit, summary


def write_outputs(
    input_path: Path,
    csv_output: Path | None,
    audit_output: Path | None,
    summary_output: Path | None,
    target_per_class: int,
    random_seed: int,
    k_neighbors: int,
) -> dict:
    dataset = load_dataset(input_path)
    augmented, audit, summary = augment_dataset(
        df=dataset,
        target_per_class=target_per_class,
        random_seed=random_seed,
        k_neighbors=k_neighbors,
    )
    summary["input"] = str(input_path)

    if csv_output is not None:
        csv_output.parent.mkdir(parents=True, exist_ok=True)
        augmented.round(6).to_csv(csv_output, index=False)

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
        description="Create interpolated synthetic rows until classes are balanced."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path)
    parser.add_argument("--audit-output", type=Path)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--target-per-class", type=int, default=350)
    parser.add_argument("--random-seed", type=int, default=20260520)
    parser.add_argument("--k-neighbors", type=int, default=5)
    args = parser.parse_args()

    summary = write_outputs(
        input_path=args.input,
        csv_output=args.csv_output,
        audit_output=args.audit_output,
        summary_output=args.summary_output,
        target_per_class=args.target_per_class,
        random_seed=args.random_seed,
        k_neighbors=args.k_neighbors,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
