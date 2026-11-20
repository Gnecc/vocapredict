# Red semántica e inferencia demostrativa

Este módulo representa alumnos, bloques de aptitud y carreras con NetworkX.
Permite buscar alumnos, consultar relaciones y puntajes, y visualizar el grafo.
La inferencia usa [RDFLib](https://github.com/RDFLib/rdflib) y
[OWL-RL](https://github.com/RDFLib/OWL-RL), ambos proyectos de código abierto.

## Ejecutar

Desde `backend/red_semantica/`:

```bash
python -m pip install -r requirements.txt
python red_semantica.py
```

La opción **9** del menú ejecuta la inferencia. También puede usarse directamente:

```bash
python inferencia.py
```

## Regla de inferencia

`inferencia.py` convierte las instancias y relaciones a un grafo RDF. Cada
evaluación se representa con alumno, bloque y puntaje. Si una aptitud tiene un
puntaje de al menos **85**, se declara `alumno destacaEn bloque`. OWL-RL aplica
la cadena de propiedades:

```text
destacaEn + importantePara -> afinidadCon
```

Por ejemplo, si un alumno destaca en Cálculo y Cálculo es importante para
Ingeniería en Computación, se infiere una afinidad con esa carrera. La salida
muestra el puntaje y la aptitud que justifican cada relación. La carrera
sugerida previamente en el ejemplo **no interviene** en la regla.

El umbral de 85 es solo para la demostración. Los cinco alumnos y sus puntajes
se generan como datos de ejemplo; no se ha validado que una afinidad inferida
prediga satisfacción o éxito profesional. El bloque de situación socioeconómica
no cuenta como aptitud para esta inferencia. La inferencia no está conectada a
la API de predicción ni al frontend.

## Poblar desde el CSV existente

El conjunto `backend/data/conjunto_de_datos_aumentado_75_sintetico_amai.csv`
contiene **1,400 perfiles**: 350 originales y 1,050 sintéticos. Sus nueve
columnas de intereses corresponden a los bloques `b1`–`b9`, pero sus puntajes
están normalizados entre 0 y 1. No contiene nombres ni números de control; por
eso el importador crea instancias `PerfilVocacional`, no `Alumno`. La columna
`CARRERA_ACTUAL` se conserva como `etiquetaDelDataset` porque procede del
reetiquetado histórico, no de una carrera declarada o recomendación validada.
El valor AMAI se guarda como dato aparte y no participa en la regla de aptitud.

Desde la raíz del proyecto:

```bash
backend/.venv/bin/python backend/red_semantica/poblar_ontologia.py --perfil 3
```

El comando genera `backend/artifacts/perfiles_vocacionales.owl` en **RDF/XML**,
que puede abrirse como ontología OWL. También vuelve a leer ese archivo y, con
`--perfil`, ejecuta OWL-RL sobre un perfil a la vez. Esto evita expandir toda
la ontología de 1,400 perfiles al consultar un solo registro. La relación
`destacaEn` usa **0.85** como umbral demostrativo para los puntajes normalizados.

La procedencia de cada fila está en `procedencia_perfiles.csv`: indica si es
original o sintética, su fila fuente y una firma SHA-256 de las columnas del
CSV. El importador verifica esa firma y rechaza archivos desalineados. Las
relaciones bloque–carrera siguen siendo las del ejemplo original y requieren
revisión antes de interpretarse como recomendaciones reales.
