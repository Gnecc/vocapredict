#!/usr/bin/env python3
"""Build one auditable VocaPredict/RIASEC table without imputing instruments.

The six RIASEC scores are means of eight 1–5 answers divided by five. A
declared university major is kept distinct from a generated VocaPredict label.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
DEFAULT_RIASEC = Path(
    "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/RIASEC_data12Dec2018/data.csv"
)
AREAS = "RIASEC"
QUESTIONS = [f"{area}{number}" for area in AREAS for number in range(1, 9)]
SCORE_COLUMNS = [f"riasec_{area}" for area in AREAS]
VOCA_FEATURES = [
    "calculo", "C. FísICO", "C. BiológICO", "MecanICO", "Servicio social",
    "Literario", "Persuasivo", "ArtístICO", "Musical", "valor_amai_normalizado",
]
FIELDS = [
    "source", "source_row_id", "voca_parent_row_id", "voca_neighbor_row_id",
    "instrument", "is_synthetic", "label_type",
    "major_raw", "career_declared_code", "career_generated_code", "career_code",
    "career_name", "country", "age", "riasec_eligible", "exclusion_reason",
    *VOCA_FEATURES, *SCORE_COLUMNS,
]
VOCA_NAMES = {
    "ICO": "Ingeniería en Computación",
    "ISC": "Licenciatura en Sistemas Computacionales",
    "LIA": "Licenciatura en Informática Administrativa",
    "LLE": "Licenciatura en Lenguas Extranjeras",
}


def normalized_major(value: str) -> str:
    """Normalize only typography; the alias catalog makes semantic decisions."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).casefold()).strip()


def load_catalog(path: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    entries = json.loads(path.read_text(encoding="utf-8"))["careers"]
    by_alias: dict[str, dict] = {}
    by_code: dict[str, dict] = {}
    for entry in entries:
        code = entry["code"]
        if code in by_code:
            raise ValueError(f"Duplicate career code: {code}")
        by_code[code] = entry
        for alias in entry["aliases"]:
            key = normalized_major(alias)
            if key in by_alias:
                raise ValueError(f"Duplicate major alias: {alias}")
            by_alias[key] = entry
    return by_alias, by_code


def riasec_scores(row: dict[str, str]) -> list[str] | None:
    scores = []
    for area in AREAS:
        values = []
        for number in range(1, 9):
            raw = (row.get(f"{area}{number}") or "").strip()
            if raw not in {"1", "2", "3", "4", "5"}:
                return None
            values.append(int(raw))
        scores.append(f"{sum(values) / 40:.6f}")
    return scores


def valid_age(value: str) -> bool:
    try:
        age = float(value)
    except (TypeError, ValueError):
        return False
    return 13 <= age <= 100 and age.is_integer()


def read_riasec(path: Path, by_alias: dict[str, dict], min_count: int):
    """Read twice to apply a fixed minimum per canonical career."""
    candidate_counts: Counter[str] = Counter()
    total = 0
    invalid_interest = invalid_age = unmapped_major = 0
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not set(QUESTIONS + ["major", "age", "country"]).issubset(reader.fieldnames or []):
            raise ValueError("RIASEC source is missing required columns")
        for row in reader:
            total += 1
            scores = riasec_scores(row)
            if scores is None:
                invalid_interest += 1
            if not valid_age(row.get("age", "")):
                invalid_age += 1
            entry = by_alias.get(normalized_major(row.get("major") or ""))
            if entry is None:
                unmapped_major += 1
            if scores is not None and valid_age(row.get("age", "")) and entry:
                candidate_counts[entry["code"]] += 1
    retained = {code for code, count in candidate_counts.items() if count >= min_count}

    def rows():
        with path.open(encoding="utf-8", newline="") as handle:
            for number, row in enumerate(csv.DictReader(handle, delimiter="\t"), start=2):
                scores = riasec_scores(row)
                age_ok = valid_age(row.get("age", ""))
                raw_major = row.get("major") or ""
                entry = by_alias.get(normalized_major(raw_major))
                code = entry["code"] if entry else ""
                # The first failed gate gives one auditable, mutually exclusive reason.
                if scores is None:
                    reason = "invalid_interest"
                elif not age_ok:
                    reason = "invalid_age"
                elif entry is None:
                    reason = "major_unmapped_or_empty"
                elif code not in retained:
                    reason = "career_below_min_count"
                else:
                    reason = ""
                result = {
                    "source": "openpsychometrics_riasec",
                    "source_row_id": number,
                    "instrument": "RIASEC",
                    "is_synthetic": 0,
                    "label_type": "declared_major" if raw_major.strip() else "none",
                    "major_raw": raw_major,
                    "career_declared_code": code,
                    "career_code": code,
                    "career_name": entry["name"] if entry else "",
                    "country": (row.get("country") or "").strip(),
                    "age": (row.get("age") or "").strip(),
                    "riasec_eligible": int(not reason),
                    "exclusion_reason": reason,
                }
                if scores is not None:
                    result.update(zip(SCORE_COLUMNS, scores))
                yield result

    source_quality = {
        "source_rows": total,
        "invalid_interest_rows": invalid_interest,
        "invalid_age_rows": invalid_age,
        "unmapped_or_empty_major_rows": unmapped_major,
        "candidate_counts_before_minimum": dict(sorted(candidate_counts.items())),
        "minimum_per_career": min_count,
    }
    return rows(), source_quality


def read_voca(path: Path, audit_path: Path):
    with path.open(encoding="utf-8", newline="") as data, audit_path.open(
        encoding="utf-8", newline=""
    ) as audit:
        data_rows = csv.DictReader(data)
        audit_rows = csv.DictReader(audit)
        for number, (row, provenance) in enumerate(zip(data_rows, audit_rows), start=2):
            if int(provenance["augmented_row_excel_1based"]) != number:
                raise ValueError(f"Voca audit row mismatch at {number}")
            code = row["CARRERA_ACTUAL"].strip()
            if code != provenance["label"].strip():
                raise ValueError(f"Voca label mismatch at {number}")
            if code not in VOCA_NAMES:
                raise ValueError(f"Unknown Voca career: {code}")
            origin = provenance["origin"]
            if origin not in {"real", "synthetic"}:
                raise ValueError(f"Unknown origin: {origin}")
            result = {
                "source": "vocapredict_augmented",
                "source_row_id": number,
                "voca_parent_row_id": provenance["source_row_excel_1based"],
                "voca_neighbor_row_id": provenance["neighbor_row_excel_1based"],
                "instrument": "Hereford",
                "is_synthetic": int(origin == "synthetic"),
                "label_type": "generated_label",
                "career_generated_code": code,
                "career_code": code,
                "career_name": VOCA_NAMES[code],
                "riasec_eligible": 0,
                "exclusion_reason": "different_instrument",
            }
            result.update({column: row[column] for column in VOCA_FEATURES})
            yield result
        if next(data_rows, None) is not None or next(audit_rows, None) is not None:
            raise ValueError("Voca dataset and audit have different row counts")


def build(args: argparse.Namespace) -> dict:
    by_alias, by_code = load_catalog(args.catalog)
    riasec_rows, quality = read_riasec(args.riasec, by_alias, args.min_count)
    reason_counts: Counter[str] = Counter()
    voca_counts: Counter[str] = Counter()
    eligible_counts: Counter[str] = Counter()
    eligible_country: Counter[str] = Counter()
    eligible_country_career: dict[str, Counter[str]] = defaultdict(Counter)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in read_voca(args.voca, args.audit):
            writer.writerow(row)
            voca_counts["synthetic" if row["is_synthetic"] else "original"] += 1
        for row in riasec_rows:
            writer.writerow(row)
            reason_counts[row["exclusion_reason"] or "eligible"] += 1
            if row["riasec_eligible"]:
                code, country = row["career_code"], row["country"] or "unknown"
                eligible_counts[code] += 1
                eligible_country[country] += 1
                eligible_country_career[country][code] += 1
    country_report_set = {country for country, _ in eligible_country.most_common(10)} | {"MX"}
    report = {
        "sources": {"riasec": str(args.riasec), "vocapredict": str(args.voca)},
        "unified_rows": quality["source_rows"] + sum(voca_counts.values()),
        "voca_rows": dict(voca_counts),
        "riasec_quality_overlapping": quality,
        "riasec_exclusion_reason_exclusive": dict(sorted(reason_counts.items())),
        "riasec_eligible_by_career": {
            code: {"name": by_code[code]["name"], "rows": count,
                   "aliases": by_code[code]["aliases"]}
            for code, count in sorted(eligible_counts.items())
        },
        "riasec_eligible_by_country": dict(eligible_country.most_common()),
        "riasec_eligible_by_career_for_top_countries_and_MX": {
            country: dict(sorted(counts.items()))
            for country, counts in sorted(eligible_country_career.items())
            if country in country_report_set
        },
        "score_definition": "mean of eight 1–5 answers divided by 5, for each RIASEC area",
        "label_warning": "RIASEC major is self-declared university study, not a validated recommendation; Voca labels were generated/relabelled.",
    }
    args.summary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--riasec", type=Path, default=DEFAULT_RIASEC)
    parser.add_argument("--voca", type=Path, default=BACKEND / "data/conjunto_de_datos_aumentado_75_sintetico_amai.csv")
    parser.add_argument("--audit", type=Path, default=BACKEND / "data/auditoria_aumento_75_sintetico.csv")
    parser.add_argument("--catalog", type=Path, default=BACKEND / "data/riasec_career_catalog.json")
    parser.add_argument("--output", type=Path, default=BACKEND / "data/vocapredict_unificado_riasec.csv")
    parser.add_argument("--summary", type=Path, default=BACKEND / "data/riasec_preparation_summary.json")
    parser.add_argument("--min-count", type=int, default=100)
    args = parser.parse_args()
    if args.min_count < 1:
        parser.error("--min-count must be positive")
    result = build(args)
    print(json.dumps({"unified_rows": result["unified_rows"],
                      "eligible": result["riasec_exclusion_reason_exclusive"].get("eligible", 0),
                      "careers": len(result["riasec_eligible_by_career"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
