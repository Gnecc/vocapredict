import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FORM_PATH = DATA_DIR / "Respuestas_de_formulario.csv"
BASE_PATH = DATA_DIR / "respuestas_chicoloapan_172_final.csv"
OUTPUT_PATH = DATA_DIR / "respuestas_chicoloapan_unificadas.csv"

FORM_COLUMN_INDEXES = [
    1,   # No. de cuenta / control
    2,   # Año de nacimiento
    3,   # Grado que cursas actualmente
    4,   # Ingreso familiar mensual
    5,   # Ingreso personal mensual
    6,   # Estudios del jefe o jefa del hogar
    8,   # Ocupación actual del padre
    9,   # Ocupación actual de la madre
    22,  # Automóviles
    10,  # Servicios y bienes
    23,  # Internet
    11,  # Cuartos para dormir
    12,  # Personas en el hogar
    13,  # Baños completos
    14,  # Personas de 14 años o más que trabajan
    15,  # Carne
    16,  # Huevos
    17,  # Leche
    18,  # Frutas y verduras
    19,  # Frijoles/arroz/lentejas
    20,  # Pan
    21,  # Cereales
]


def read_csv(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.reader(csv_file))


def main() -> None:
    base_rows = read_csv(BASE_PATH)
    form_rows = read_csv(FORM_PATH)

    header = base_rows[0]
    if len(header) != len(FORM_COLUMN_INDEXES):
        raise ValueError("The canonical schema no longer matches the form mapping.")

    # The first three form submissions were test records.
    mapped_form_rows = [
        [row[index].strip() for index in FORM_COLUMN_INDEXES]
        for row in form_rows[4:]
    ]

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(base_rows[1:])
        writer.writerows(mapped_form_rows)

    print(
        f"Created {OUTPUT_PATH} with "
        f"{len(base_rows) - 1} existing records and "
        f"{len(mapped_form_rows)} form records."
    )


if __name__ == "__main__":
    main()
