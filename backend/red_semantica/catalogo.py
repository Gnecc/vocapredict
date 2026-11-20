"""Identificadores compartidos por la demostración y el importador CSV."""

CARRERAS = (
    ("c1", "Ingenieria en Computacion (ICO)", "ICO"),
    ("c2", "Licenciatura en Informatica Administrativa (LIA)", "LIA"),
    ("c3", "Ingenieria en Sistemas Inteligentes (ISC)", "ISC"),
    ("c4", "Licenciatura en Lenguas (LLE)", "LLE"),
)

# Vínculos provisionales: áreas con valor >= 0.70 en los perfiles objetivo de
# backend/scripts/relabel_dataset.py. Son rasgos de plantillas históricas, no
# requisitos académicos de las carreras ni relaciones validadas por orientadores.
BLOQUES = (
    ("b1", "Calculo", ("c1", "c3")),
    ("b2", "C. Fisico", ("c1", "c3")),
    ("b3", "C. Biologico", ()),
    ("b4", "Mecanico", ("c1", "c3")),
    ("b5", "Servicio social", ("c2", "c4")),
    ("b6", "Literario", ("c4",)),
    ("b7", "Persuasivo", ("c2", "c4")),
    ("b8", "Artistico", ()),
    ("b9", "Musical", ()),
    ("b10", "Situacion socioeconomica", ()),
)
