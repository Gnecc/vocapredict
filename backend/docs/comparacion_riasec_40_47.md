# Comparación RIASEC de 40 y 47 carreras

Los modelos se entrenaron con 32,330 y 33,881 casos.
Comparten 8,083 casos de prueba originales. Para las siete clases nuevas
se reservaron otros 385 casos. Las 12 correcciones MX se usaron para
entrenar la versión ampliada. Cada modelo usa los seis puntajes y el mismo
clasificador con pesos de clase. El objetivo observado es la carrera declarada.

| Modelo y prueba | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Top 3 por frecuencia |
|---|---:|---:|---:|---:|---:|
| 40 · compartida | 8,083 | 28.5% | 47.1% | 21.3% | 43.0% |
| 47 · compartida | 8,083 | 27.9% | 45.9% | 20.0% | 43.0% |
| 47 · nuevas | 385 | 4.4% | 20.8% | 12.8% | 0.0% |
| 47 · completa | 8,468 | 26.8% | 44.8% | 19.0% | 41.0% |

## Resultados por carrera

Top 1 y Top 3 indican el porcentaje de casos de cada carrera en los que
la etiqueta declarada apareció en primera posición o entre las tres primeras.
Las siete clases nuevas solo se evalúan con el modelo de 47.

| Carrera | Perfiles disponibles | Casos de prueba | Top 1 · 40 | Top 3 · 40 | Top 1 · 47 | Top 3 · 47 |
|---|---:|---:|---:|---:|---:|---:|
| Administración Hotelera | 110 | 22 | — | — | 0.0% | 0.0% |
| Administración de empresas | 1,487 | 297 | 16.8% | 52.5% | 17.5% | 50.5% |
| Antropología | 297 | 59 | 1.7% | 8.5% | 1.7% | 10.2% |
| Arquitectura | 511 | 102 | 10.8% | 23.5% | 10.8% | 19.6% |
| Biología | 2,018 | 404 | 41.3% | 71.5% | 41.6% | 71.5% |
| Bioquímica | 254 | 51 | 0.0% | 13.7% | 0.0% | 13.7% |
| Ciencias Ambientales | 195 | 39 | — | — | 0.0% | 0.0% |
| Ciencias de la computación | 1,202 | 240 | 17.5% | 28.3% | 16.7% | 27.9% |
| Ciencias políticas | 653 | 131 | 0.0% | 0.8% | 0.0% | 0.8% |
| Cinematografía | 131 | 26 | — | — | 3.8% | 30.8% |
| Comunicación | 1,092 | 219 | — | — | 7.3% | 29.2% |
| Contaduría | 1,399 | 280 | 39.6% | 55.0% | 39.6% | 54.3% |
| Criminología | 175 | 35 | 0.0% | 0.0% | 0.0% | 0.0% |
| Derecho | 1,048 | 209 | 1.4% | 16.3% | 1.4% | 9.6% |
| Diseño gráfico | 260 | 52 | 3.8% | 11.5% | 1.9% | 3.8% |
| Economía | 1,042 | 208 | 0.5% | 8.2% | 0.0% | 6.7% |
| Educación | 1,785 | 357 | 0.6% | 42.0% | 0.3% | 38.9% |
| Educación Primaria | 145 | 29 | — | — | 0.0% | 3.4% |
| Enfermería | 2,197 | 439 | 15.9% | 53.1% | 15.9% | 52.8% |
| Farmacia | 229 | 46 | 0.0% | 2.2% | 0.0% | 2.2% |
| Filosofía | 414 | 83 | 1.2% | 14.5% | 1.2% | 12.0% |
| Finanzas | 734 | 147 | 0.7% | 21.1% | 0.7% | 20.4% |
| Física | 451 | 90 | 6.7% | 20.0% | 6.7% | 20.0% |
| Geografía | 210 | 42 | 0.0% | 0.0% | 0.0% | 0.0% |
| Historia | 924 | 185 | 1.1% | 9.2% | 0.5% | 8.6% |
| Historia del Arte | 115 | 23 | — | — | 0.0% | 0.0% |
| Ingeniería civil | 1,023 | 205 | 16.1% | 45.9% | 16.1% | 45.9% |
| Ingeniería de software | 120 | 24 | 0.0% | 0.0% | 0.0% | 0.0% |
| Ingeniería eléctrica | 463 | 93 | 2.2% | 21.5% | 2.2% | 21.5% |
| Ingeniería en computación | 284 | 57 | 0.0% | 0.0% | 0.0% | 0.0% |
| Ingeniería industrial | 116 | 23 | 0.0% | 0.0% | 0.0% | 0.0% |
| Ingeniería mecánica | 724 | 144 | 32.6% | 50.0% | 31.2% | 51.4% |
| Ingeniería química | 406 | 81 | 0.0% | 4.9% | 0.0% | 6.2% |
| Justicia penal | 874 | 175 | 0.0% | 12.6% | 0.0% | 11.4% |
| Kinesiología | 265 | 53 | 0.0% | 11.3% | 0.0% | 11.3% |
| Lingüística | 193 | 39 | 0.0% | 0.0% | 0.0% | 0.0% |
| Matemáticas | 786 | 157 | 2.5% | 14.0% | 2.5% | 14.0% |
| Medicina | 752 | 150 | 0.0% | 14.0% | 0.0% | 14.0% |
| Mercadotecnia | 872 | 174 | 17.2% | 31.0% | 13.8% | 25.3% |
| Música | 461 | 92 | 35.9% | 55.4% | 22.8% | 52.2% |
| Periodismo | 360 | 72 | 0.0% | 13.9% | 0.0% | 0.0% |
| Psicología | 13,146 | 2,629 | 64.1% | 81.8% | 63.0% | 80.9% |
| Química | 544 | 109 | 0.0% | 15.6% | 0.0% | 15.6% |
| Relaciones internacionales | 219 | 44 | 0.0% | 0.0% | 0.0% | 0.0% |
| Sociología | 856 | 171 | 0.0% | 1.8% | 0.0% | 1.8% |
| Teatro | 136 | 27 | — | — | 0.0% | 25.9% |
| Trabajo social | 671 | 134 | 1.5% | 28.4% | 1.5% | 26.9% |
