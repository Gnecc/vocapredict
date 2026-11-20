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
