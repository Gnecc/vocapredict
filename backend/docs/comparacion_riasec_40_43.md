# Comparación RIASEC de 40 y 43 carreras

La versión de 43 agrega Comunicación, Cinematografía y Teatro. Ambos modelos
usan los mismos perfiles de entrenamiento de las 40 clases originales y la
misma regresión logística con pesos de clase. El predictor de 43 se entrena
con 33,417 casos, incluidos 1,087 de las tres clases nuevas.
Las 12 correcciones del conjunto de 47 quedaron fuera de este experimento
para medir específicamente el efecto de añadir las tres clases.
Los conjuntos de prueba conservan los identificadores de la comparación anterior.
Las tres carreras se eligieron con resultados de esa misma prueba, así que
el resultado es exploratorio y requiere una evaluación nueva para confirmarse.

| Modelo | Grupo | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Carreras con cero en top 3 |
|---|---|---:|---:|---:|---:|---:|
| 40 | Compartidas | 8,083 | 28.5% | 47.1% | 21.3% | 7 |
| 40 | Nuevas | 272 | 0.0% | 0.0% | 0.0% | 3 |
| 40 | Todas | 8,355 | 27.6% | 45.6% | 19.9% | 10 |
| 43 | Compartidas | 8,083 | 27.9% | 45.8% | 20.0% | 8 |
| 43 | Nuevas | 272 | 6.2% | 29.4% | 28.8% | 0 |
| 43 | Todas | 8,355 | 27.2% | 45.3% | 20.6% | 8 |

## Resultados por carrera

Cada celda indica aciertos sobre el total de casos de prueba de esa carrera.
El modelo de 40 carece de las tres clases nuevas.

| Carrera | Top 1 · 40 | Top 3 · 40 | Top 1 · 43 | Top 3 · 43 |
|---|---:|---:|---:|---:|
| Administración de empresas | 50/297 | 156/297 | 52/297 | 148/297 |
| Antropología | 1/59 | 5/59 | 1/59 | 6/59 |
| Arquitectura | 11/102 | 24/102 | 11/102 | 20/102 |
| Biología | 167/404 | 289/404 | 167/404 | 289/404 |
| Bioquímica | 0/51 | 7/51 | 0/51 | 7/51 |
| Ciencias de la computación | 42/240 | 68/240 | 41/240 | 67/240 |
| Ciencias políticas | 0/131 | 1/131 | 0/131 | 1/131 |
| Cinematografía | — | — | 1/26 | 8/26 |
| Comunicación | — | — | 16/219 | 65/219 |
| Contaduría | 111/280 | 154/280 | 112/280 | 152/280 |
| Criminología | 0/35 | 0/35 | 0/35 | 0/35 |
| Derecho | 3/209 | 34/209 | 3/209 | 20/209 |
| Diseño gráfico | 2/52 | 6/52 | 1/52 | 2/52 |
| Economía | 1/208 | 17/208 | 1/208 | 13/208 |
| Educación | 2/357 | 150/357 | 1/357 | 140/357 |
| Enfermería | 70/439 | 233/439 | 71/439 | 232/439 |
| Farmacia | 0/46 | 1/46 | 0/46 | 1/46 |
| Filosofía | 1/83 | 12/83 | 1/83 | 10/83 |
| Finanzas | 1/147 | 31/147 | 1/147 | 31/147 |
| Física | 6/90 | 18/90 | 6/90 | 18/90 |
| Geografía | 0/42 | 0/42 | 0/42 | 0/42 |
| Historia | 2/185 | 17/185 | 1/185 | 16/185 |
| Ingeniería civil | 33/205 | 94/205 | 33/205 | 93/205 |
| Ingeniería de software | 0/24 | 0/24 | 0/24 | 0/24 |
| Ingeniería eléctrica | 2/93 | 20/93 | 2/93 | 21/93 |
| Ingeniería en computación | 0/57 | 0/57 | 0/57 | 0/57 |
| Ingeniería industrial | 0/23 | 0/23 | 0/23 | 0/23 |
| Ingeniería mecánica | 47/144 | 72/144 | 46/144 | 72/144 |
| Ingeniería química | 0/81 | 4/81 | 0/81 | 4/81 |
| Justicia penal | 0/175 | 22/175 | 0/175 | 20/175 |
| Kinesiología | 0/53 | 6/53 | 0/53 | 6/53 |
| Lingüística | 0/39 | 0/39 | 0/39 | 0/39 |
| Matemáticas | 4/157 | 22/157 | 4/157 | 22/157 |
| Medicina | 0/150 | 21/150 | 0/150 | 21/150 |
| Mercadotecnia | 30/174 | 54/174 | 23/174 | 44/174 |
| Música | 33/92 | 51/92 | 21/92 | 48/92 |
| Periodismo | 0/72 | 10/72 | 0/72 | 0/72 |
| Psicología | 1685/2629 | 2150/2629 | 1656/2629 | 2127/2629 |
| Química | 0/109 | 17/109 | 0/109 | 16/109 |
| Relaciones internacionales | 0/44 | 0/44 | 0/44 | 0/44 |
| Sociología | 0/171 | 3/171 | 0/171 | 3/171 |
| Teatro | — | — | 0/27 | 7/27 |
| Trabajo social | 2/134 | 38/134 | 2/134 | 35/134 |
