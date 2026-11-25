# RIASEC: familias vocacionales y transferencia entre países

Se compara la predicción de 40 carreras con dos estrategias de agrupación.
Una suma los puntajes de carreras por familia y la otra aprende las familias
directamente. La variante jerárquica multiplica el puntaje de cada familia
por la probabilidad de la carrera dentro de ella, sin descartar familias.
Las agrupaciones se definieron por disciplina antes de la prueba.
La etiqueta sigue siendo la carrera o familia declarada, medida en tareas distintas.
La referencia por frecuencia usa las clases más frecuentes del entrenamiento.

La prueba histórica se ha usado antes. En las pruebas por país se excluye del
entrenamiento cada fila con el código evaluado. Esos códigos reflejan ubicación
de conexión. La evaluación MX es exploratoria por su tamaño y procedencia.
Estos ejercicios reutilizan la colección original y no sustituyen una prueba prospectiva.

## Familias

| Familia | Carreras |
|---|---|
| Administración y economía | Contaduría, Administración de empresas, Economía, Finanzas, Mercadotecnia |
| Arte y diseño | Arquitectura, Diseño gráfico, Música |
| Ciencias naturales y matemáticas | Bioquímica, Biología, Química, Matemáticas, Física |
| Ciencias sociales | Antropología, Geografía, Relaciones internacionales, Ciencias políticas, Sociología, Trabajo social |
| Computación y software | Ingeniería de software, Ingeniería en computación, Ciencias de la computación |
| Derecho y justicia | Criminología, Justicia penal, Derecho |
| Educación | Educación |
| Humanidades y comunicación | Historia, Periodismo, Lingüística, Filosofía |
| Ingeniería | Ingeniería química, Ingeniería civil, Ingeniería eléctrica, Ingeniería industrial, Ingeniería mecánica |
| Salud y comportamiento | Kinesiología, Medicina, Enfermería, Farmacia, Psicología |

## Resultados

| Partición | Casos | Objetivo | Modelo | Top 1 | Top 3 | Exactitud equilibrada |
|---|---:|---|---|---:|---:|---:|
| Histórica | 8,083 | Carrera | Por frecuencia | 32.5% | 43.0% | 2.5% |
| Histórica | 8,083 | Carrera | Logística ponderada · 6 puntajes | 28.5% | 47.1% | 8.3% |
| Histórica | 8,083 | Carrera | Logística directa · 48 respuestas | 36.3% | 57.2% | 8.5% |
| Histórica | 8,083 | Carrera | Logística jerárquica · 48 respuestas | 36.2% | 56.6% | 7.9% |
| Histórica | 8,083 | Familia | Por frecuencia | 41.0% | 64.8% | 10.0% |
| Histórica | 8,083 | Familia | Agrupando puntajes del modelo de carreras | 49.3% | 75.8% | 24.0% |
| Histórica | 8,083 | Familia | Modelo directo de familias · 48 respuestas | 48.8% | 75.0% | 22.8% |
| País fuera · US | 22,725 | Carrera | Por frecuencia | 37.0% | 38.8% | 2.5% |
| País fuera · US | 22,725 | Carrera | Logística ponderada · 6 puntajes | 32.7% | 50.0% | 7.9% |
| País fuera · US | 22,725 | Carrera | Logística directa · 48 respuestas | 39.6% | 58.5% | 9.2% |
| País fuera · US | 22,725 | Carrera | Logística jerárquica · 48 respuestas | 39.2% | 57.8% | 8.3% |
| País fuera · US | 22,725 | Familia | Por frecuencia | 46.9% | 62.2% | 10.0% |
| País fuera · US | 22,725 | Familia | Agrupando puntajes del modelo de carreras | 52.4% | 77.5% | 25.2% |
| País fuera · US | 22,725 | Familia | Modelo directo de familias · 48 respuestas | 51.9% | 76.9% | 24.1% |
| País fuera · MX | 85 | Carrera | Por frecuencia | 12.9% | 18.8% | 3.1% |
| País fuera · MX | 85 | Carrera | Logística ponderada · 6 puntajes | 16.5% | 37.6% | 11.4% |
| País fuera · MX | 85 | Carrera | Logística directa · 48 respuestas | 20.0% | 44.7% | 13.6% |
| País fuera · MX | 85 | Carrera | Logística jerárquica · 48 respuestas | 20.0% | 44.7% | 10.8% |
| País fuera · MX | 85 | Familia | Por frecuencia | 20.0% | 49.4% | 10.0% |
| País fuera · MX | 85 | Familia | Agrupando puntajes del modelo de carreras | 38.8% | 71.8% | 26.8% |
| País fuera · MX | 85 | Familia | Modelo directo de familias · 48 respuestas | 40.0% | 74.1% | 27.3% |

## Aciertos por familia en la prueba histórica

| Familia | Casos | Top 1 | Top 3 |
|---|---:|---:|---:|
| Administración y economía | 1,106 | 50.6% | 84.6% |
| Arte y diseño | 246 | 15.9% | 46.7% |
| Ciencias naturales y matemáticas | 811 | 24.0% | 75.8% |
| Ciencias sociales | 581 | 0.9% | 52.8% |
| Computación y software | 321 | 16.5% | 42.7% |
| Derecho y justicia | 419 | 1.0% | 31.0% |
| Educación | 357 | 4.5% | 42.9% |
| Humanidades y comunicación | 379 | 7.9% | 40.4% |
| Ingeniería | 546 | 31.5% | 65.0% |
| Salud y comportamiento | 3,317 | 87.7% | 97.3% |

## Primera opción con abstención

Se ajusta una logística directa con 48 respuestas. En una partición interna
se elige el umbral de menor valor, en pasos de 0.01 de 0.35 a 0.95, que alcance
80 % de aciertos en al menos 100 casos aceptados. En prueba el modelo solo
reporta una carrera si su puntuación máxima supera o iguala ese umbral.
Se muestran tanto la exactitud de las respuestas emitidas como su cobertura.

| Partición | Umbral | Aceptados en validación | Exactitud validación | Aciertos / sugerencias | Exactitud prueba | Cobertura prueba | Sugerencia más frecuente |
|---|---:|---:|---:|---:|---:|---:|---|
| Histórica | 0.72 | 171 | 81.3% | 201/238 | 84.5% | 2.9% | Psicología (220/238) |
| País fuera · US | Sin umbral | — | — | — | — | — | — |
| País fuera · MX | 0.69 | 336 | 82.4% | 2/2 | 100.0% | 2.4% | Psicología (2/2) |

## Confusiones en la prueba histórica

Las confusiones entre carreras de una misma familia suman 901 de 5,146 errores en primera opción de la logística directa.

| Carrera declarada | Primera opción errónea | Casos |
|---|---|---:|
| Enfermería | Psicología | 279 |
| Educación | Psicología | 274 |
| Biología | Psicología | 211 |
| Administración de empresas | Psicología | 160 |
| Derecho | Psicología | 157 |
| Sociología | Psicología | 152 |
| Historia | Psicología | 137 |
| Justicia penal | Psicología | 133 |
| Contaduría | Psicología | 132 |
| Trabajo social | Psicología | 120 |
| Economía | Psicología | 114 |
| Mercadotecnia | Psicología | 106 |

Desde `backend/`:

```bash
python3 -m scripts.compare_riasec_families --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv
```
