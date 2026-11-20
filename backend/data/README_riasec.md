# Conjunto unificado VocaPredict–RIASEC

Se genera con:

```bash
backend/.venv/bin/python backend/scripts/prepare_riasec_dataset.py
```

El archivo `vocapredict_unificado_riasec.csv` conserva las 145,828 respuestas
RIASEC y las 1,400 filas del conjunto aumentado de VocaPredict. Sus campos
`source`, `source_row_id`, `instrument`, `is_synthetic` y `label_type` indican la
procedencia. En VocaPredict se verificó cada fila contra
`auditoria_aumento_75_sintetico.csv`; `voca_parent_row_id` y
`voca_neighbor_row_id` permiten rastrear el aumento. Son 350 filas originales
y 1,050 sintéticas. Su `career_generated_code` es una etiqueta generada a
partir del reetiquetado existente; no se presenta como carrera declarada.

En RIASEC, `major_raw` es la respuesta libre a la pregunta sobre la carrera
universitaria estudiada. `career_declared_code` aparece solo cuando el texto
coincide con una regla explícita de `riasec_career_catalog.json`. Las reglas
normalizan Unicode, mayúsculas y espacios, pero no hacen semejanza aproximada
ni agrupan términos amplios como `business`, `engineering` o `medical`.
`career_code` recoge la etiqueta utilizable dentro de cada instrumento;
`label_type` indica su significado. Ninguna de estas etiquetas confirma que
una carrera sea una recomendación satisfactoria.

Cada escala `riasec_R/I/A/S/E/C` es el promedio de sus ocho respuestas 1–5
dividido por 5. La puntuación solo se calcula con las 48 respuestas válidas;
su intervalo es 0.2–1. Una fila RIASEC es elegible para entrenamiento si
cumple las 48 respuestas válidas, edad entera entre 13 y 100, `major` mapeado
y al menos 100 filas candidatas para su carrera. Las 9 columnas Hereford y
AMAI quedan vacías en RIASEC; las seis RIASEC quedan vacías en VocaPredict.
No se sintetiza AMAI ni se convierten las escalas entre cuestionarios.

`riasec_preparation_summary.json` contiene los conteos reproducibles por
carrera y país. `riasec_quality_overlapping` informa problemas que pueden
coexistir en una fila; `riasec_exclusion_reason_exclusive` asigna una sola
razón por fila, en orden: intereses inválidos, edad inválida, carrera sin
mapeo y carrera con menos de 100 casos. En esta versión quedan 40,413 filas
RIASEC elegibles para 40 carreras. El país procede de la ubicación de red
según el codebook, no de una nacionalidad verificada.

Para añadir carreras, revise las expresiones originales, agregue alias
explícitos al catálogo y regenere los archivos. Las respuestas ambiguas
deben permanecer sin mapeo hasta contar con una justificación académica.
