# Revisión de la ampliación RIASEC

## Alcance y procedencia

Se preparó un archivo unificado de 147,228 filas: 145,828 de OpenPsychometrics RIASEC y 1,400 del conjunto aumentado VocaPredict. Las filas VocaPredict incluyen 350 originales y 1,050 sintéticas. Conservan sus nueve áreas Hereford y AMAI; sus seis áreas RIASEC están vacías. Las filas RIASEC conservan el texto original `major`, país de la conexión y seis áreas calculadas; Hereford y AMAI están vacíos. Cada fila indica fuente, instrumento, tipo de etiqueta y elegibilidad. Ningún valor se fabricó para unir los instrumentos.

El catálogo `../data/riasec_career_catalog.json` enumera cada alias admitido. Solo normaliza espacios, Unicode y mayúsculas antes de comparar textos exactos. `major` es una carrera universitaria **declarada**, no una recomendación validada. Las etiquetas de VocaPredict son **generadas** por su proceso previo de reetiquetado.

## Selección de datos

Una fila RIASEC es elegible cuando tiene sus 48 respuestas de interés entre 1 y 5, edad entera entre 13 y 100, carrera declarada que coincide con un alias explícito y al menos 100 filas candidatas para esa carrera. Cada área es la media de ocho respuestas dividida entre cinco.

| Resultado | Filas |
| --- | ---: |
| RIASEC originales | 145,828 |
| Excluidas por intereses inválidos | 10,064 |
| Excluidas por edad, después del filtro de intereses | 77 |
| Excluidas por carrera vacía o sin mapeo, después de filtros anteriores | 95,180 |
| Excluidas por carrera con menos de 100 casos | 94 |
| RIASEC elegibles | **40,413** |
| VocaPredict conservadas, fuera del entrenamiento RIASEC | 1,400 |

Las razones de exclusión son mutuamente excluyentes y suman 145,828. El resumen `../data/riasec_preparation_summary.json` incluye problemas que se superponen, conteos por país y reglas por carrera. El archivo unificado se regenera con `backend/.venv/bin/python backend/scripts/prepare_riasec_dataset.py` desde la raíz del proyecto.

## Carreras y casos elegibles

El recobrado indicado es para la **primera** predicción de la carrera declarada en la prueba separada; no mide calidad de recomendación. El archivo `../artifacts/riasec_metrics.json` contiene precisión, recobrado y F1 completos por carrera.

| Código | Carrera | Filas | Recobrado primera opción |
| --- | --- | ---: | ---: |
| ACC | Contaduría | 1,399 | 39.6 % |
| ANT | Antropología | 297 | 1.7 % |
| ARC | Arquitectura | 509 | 10.8 % |
| BAM | Administración de empresas | 1,486 | 16.8 % |
| BCH | Bioquímica | 254 | 0.0 % |
| BIO | Biología | 2,018 | 41.3 % |
| CEN | Ingeniería química | 405 | 0.0 % |
| CENM | Ingeniería de software | 120 | 0.0 % |
| CENR | Ingeniería en computación | 284 | 0.0 % |
| CHE | Química | 544 | 0.0 % |
| CIV | Ingeniería civil | 1,023 | 16.1 % |
| CRI | Criminología | 175 | 0.0 % |
| CRJ | Justicia penal | 874 | 0.0 % |
| CSC | Ciencias de la computación | 1,201 | 17.5 % |
| ECO | Economía | 1,041 | 0.5 % |
| EDU | Educación | 1,785 | 0.6 % |
| ELE | Ingeniería eléctrica | 463 | 2.2 % |
| FIN | Finanzas | 734 | 0.7 % |
| GDE | Diseño gráfico | 260 | 3.8 % |
| GEO | Geografía | 210 | 0.0 % |
| HIS | Historia | 924 | 1.1 % |
| IND | Ingeniería industrial | 116 | 0.0 % |
| IRL | Relaciones internacionales | 219 | 0.0 % |
| JOU | Periodismo | 360 | 0.0 % |
| KIN | Kinesiología | 265 | 0.0 % |
| LAW | Derecho | 1,047 | 1.4 % |
| LIN | Lingüística | 193 | 0.0 % |
| MAT | Matemáticas | 785 | 2.5 % |
| MEC | Ingeniería mecánica | 722 | 32.6 % |
| MED | Medicina | 752 | 0.0 % |
| MKT | Mercadotecnia | 872 | 17.2 % |
| MUS | Música | 461 | 35.9 % |
| NUR | Enfermería | 2,197 | 15.9 % |
| PHA | Farmacia | 229 | 0.0 % |
| PHI | Filosofía | 414 | 1.2 % |
| PHY | Física | 451 | 6.7 % |
| POL | Ciencias políticas | 653 | 0.0 % |
| PSY | Psicología | 13,144 | 64.1 % |
| SOC | Sociología | 856 | 0.0 % |
| SWK | Trabajo social | 671 | 1.5 % |

## Evaluación y límites

Se separaron 32,330 filas para entrenamiento y 8,083 para prueba de forma estratificada antes de calcular los pesos de clase. La exactitud de primera opción fue 28.5 %; la carrera declarada apareció en las primeras tres opciones en 47.1 % de la prueba. El promedio de top tres por carrera fue 21.3 %. Aparecieron 38 de 40 carreras alguna vez en el top tres; Ingeniería en computación y Geografía no aparecieron. Diecisiete carreras tuvieron recobrado cero como primera opción. Estos resultados no acreditan que las opciones sean adecuadas para cada persona.

La prueba incluye 4,567 casos de US, con top tres de 53.3 %; 375 de GB, 35.2 %; 343 de CA, 44.9 %; y 485 de MY, 41.9 %. Las diferencias también pueden deberse a la composición de carreras en cada país. Solo 85 filas elegibles tienen país de conexión MX, insuficientes para una conclusión sólida sobre México. El país es el de la red y no una nacionalidad confirmada.

La versión nueva pregunta 48 actividades RIASEC y muestra tres carreras para explorar. El modelo antiguo Hereford sigue disponible para entrenamiento histórico, pero sus cuatro etiquetas no son equivalentes al catálogo RIASEC y no se mezclan en la nueva predicción. La API y la pantalla no muestran el puntaje del clasificador como probabilidad de aptitud o satisfacción.

## Verificación

- Preparación reproducible: 147,228 filas, IDs de fuente únicos, 350 originales y 1,050 sintéticas verificadas con la auditoría de aumento, sin puntajes inventados entre instrumentos.
- Entrenamiento RIASEC: 40,413 elegibles, partición 32,330/8,083 y métricas guardadas en `../artifacts/riasec_metrics.json`.
- API ASGI: `POST /predict` con seis puntajes responde 200 y tres carreras; cinco puntajes responden 422.
- Frontend: compilación `NODE_OPTIONS=--openssl-legacy-provider npm run build` satisfactoria; 48 preguntas, seis puntajes en orden R, I, A, S, E, C y resultado con tres carreras.
- `git diff --check` y compilación Python sin errores.

La prueba ASGI no abre un puerto. No se ejecutó una prueba visual del navegador ni un despliegue.
