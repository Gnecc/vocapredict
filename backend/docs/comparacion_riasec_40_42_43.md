# RIASEC de 42 clases con Comunicación y Periodismo agrupadas

El entrenamiento de 42 clases reutiliza los 33,417 perfiles del modelo de 43.
Agrupa 873 casos de Comunicación y 288 de Periodismo. Se conserva la regresión logística
y se recalculan los pesos por frecuencia de las 42 clases.
La prueba usa los mismos 8,083 casos compartidos y 272 nuevos.
Se conservan las etiquetas originales para desglosar resultados y se usa la etiqueta
agrupada como objetivo común. Para los modelos anteriores se asigna al grupo
la mayor puntuación de sus integrantes antes de ordenar las tres opciones distintas.
El modelo de 40 solo aporta Periodismo al grupo. También se prueba sumar las dos
puntuaciones del modelo de 43 antes de ordenar. Son puntuaciones relativas.
El de 43 ajustado usa el multiplicador histórico de Periodismo de 1.3×.
La partición se usó en estudios previos. Estos resultados son exploratorios.

| Modelo | Grupo de prueba | Casos | Top 1 | Top 3 | Top 3 promedio por clase |
|---|---|---:|---:|---:|---:|
| 40 original | Compartidos | 8,083 | 28.5% | 47.1% | 21.3% |
| 40 original | Nuevos | 272 | 0.7% | 9.2% | 3.8% |
| 40 original | Todos | 8,355 | 27.6% | 45.9% | 20.3% |
| 40 original | Fuera de Comunicación y Periodismo | 8,064 | 28.6% | 47.1% | 20.5% |
| 43 original | Compartidos | 8,083 | 28.0% | 46.1% | 20.7% |
| 43 original | Nuevos | 272 | 6.2% | 29.8% | 28.9% |
| 43 original | Todos | 8,355 | 27.3% | 45.6% | 21.1% |
| 43 original | Fuera de Comunicación y Periodismo | 8,064 | 28.0% | 46.1% | 20.9% |
| 43 ajustado | Compartidos | 8,083 | 28.0% | 46.2% | 20.8% |
| 43 ajustado | Nuevos | 272 | 6.6% | 32.4% | 30.0% |
| 43 ajustado | Todos | 8,355 | 27.3% | 45.7% | 21.1% |
| 43 ajustado | Fuera de Comunicación y Periodismo | 8,064 | 28.0% | 46.1% | 20.8% |
| 42 agrupado | Compartidos | 8,083 | 27.9% | 46.0% | 20.9% |
| 42 agrupado | Nuevos | 272 | 8.1% | 36.4% | 31.7% |
| 42 agrupado | Todos | 8,355 | 27.2% | 45.7% | 21.1% |
| 42 agrupado | Fuera de Comunicación y Periodismo | 8,064 | 27.9% | 45.9% | 20.6% |
| 43 con suma al mostrar | Compartidos | 8,083 | 26.6% | 45.6% | 21.0% |
| 43 con suma al mostrar | Nuevos | 272 | 22.1% | 51.8% | 34.7% |
| 43 con suma al mostrar | Todos | 8,355 | 26.4% | 45.8% | 20.8% |
| 43 con suma al mostrar | Fuera de Comunicación y Periodismo | 8,064 | 26.4% | 45.2% | 19.8% |

## Aciertos del grupo en el top 3

| Modelo | Periodismo original | Comunicación original | Total del grupo | Precisión del grupo |
|---|---:|---:|---:|---:|
| 40 original | 10/72 | 25/219 | 35/291 | 35/258 (13.6%) |
| 43 original | 22/72 | 66/219 | 88/291 | 88/919 (9.6%) |
| 43 ajustado | 26/72 | 73/219 | 99/291 | 99/1064 (9.3%) |
| 42 agrupado | 35/72 | 84/219 | 119/291 | 119/1276 (9.3%) |
| 43 con suma al mostrar | 54/72 | 129/219 | 183/291 | 183/2538 (7.2%) |

## Top 3 por clase agrupada

Los conteos muestran aciertos sobre el total de casos de prueba de cada clase.

| Clase | 40 original | 43 original | 43 ajustado | 42 agrupado | 43 con suma al mostrar |
|---|---:|---:|---:|---:|---:|
| Administración de empresas | 156/297 | 148/297 | 148/297 | 147/297 | 145/297 |
| Antropología | 5/59 | 6/59 | 6/59 | 6/59 | 5/59 |
| Arquitectura | 24/102 | 20/102 | 20/102 | 22/102 | 19/102 |
| Biología | 289/404 | 289/404 | 289/404 | 289/404 | 285/404 |
| Bioquímica | 7/51 | 7/51 | 7/51 | 7/51 | 7/51 |
| Ciencias de la computación | 68/240 | 67/240 | 67/240 | 67/240 | 66/240 |
| Ciencias políticas | 1/131 | 1/131 | 1/131 | 1/131 | 1/131 |
| Cinematografía | 0/26 | 8/26 | 8/26 | 8/26 | 6/26 |
| Comunicación y Periodismo | 35/291 | 88/291 | 99/291 | 119/291 | 183/291 |
| Contaduría | 154/280 | 152/280 | 152/280 | 152/280 | 149/280 |
| Criminología | 0/35 | 0/35 | 0/35 | 0/35 | 0/35 |
| Derecho | 34/209 | 20/209 | 21/209 | 18/209 | 17/209 |
| Diseño gráfico | 6/52 | 2/52 | 2/52 | 2/52 | 2/52 |
| Economía | 17/208 | 13/208 | 14/208 | 13/208 | 12/208 |
| Educación | 150/357 | 140/357 | 140/357 | 138/357 | 132/357 |
| Enfermería | 233/439 | 232/439 | 231/439 | 231/439 | 228/439 |
| Farmacia | 1/46 | 1/46 | 1/46 | 1/46 | 1/46 |
| Filosofía | 12/83 | 10/83 | 9/83 | 9/83 | 6/83 |
| Finanzas | 31/147 | 31/147 | 31/147 | 30/147 | 31/147 |
| Física | 18/90 | 18/90 | 18/90 | 18/90 | 18/90 |
| Geografía | 0/42 | 0/42 | 0/42 | 0/42 | 0/42 |
| Historia | 17/185 | 17/185 | 15/185 | 13/185 | 10/185 |
| Ingeniería civil | 94/205 | 93/205 | 93/205 | 93/205 | 93/205 |
| Ingeniería de software | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 |
| Ingeniería eléctrica | 20/93 | 21/93 | 21/93 | 20/93 | 21/93 |
| Ingeniería en computación | 0/57 | 0/57 | 0/57 | 0/57 | 0/57 |
| Ingeniería industrial | 0/23 | 0/23 | 0/23 | 0/23 | 0/23 |
| Ingeniería mecánica | 72/144 | 72/144 | 73/144 | 72/144 | 71/144 |
| Ingeniería química | 4/81 | 4/81 | 4/81 | 4/81 | 4/81 |
| Justicia penal | 22/175 | 20/175 | 21/175 | 20/175 | 17/175 |
| Kinesiología | 6/53 | 6/53 | 6/53 | 6/53 | 6/53 |
| Lingüística | 0/39 | 0/39 | 0/39 | 0/39 | 0/39 |
| Matemáticas | 22/157 | 22/157 | 22/157 | 22/157 | 22/157 |
| Medicina | 21/150 | 21/150 | 21/150 | 21/150 | 20/150 |
| Mercadotecnia | 54/174 | 44/174 | 44/174 | 43/174 | 41/174 |
| Música | 51/92 | 48/92 | 46/92 | 45/92 | 44/92 |
| Psicología | 2150/2629 | 2127/2629 | 2127/2629 | 2121/2629 | 2109/2629 |
| Química | 17/109 | 16/109 | 17/109 | 16/109 | 16/109 |
| Relaciones internacionales | 0/44 | 0/44 | 0/44 | 0/44 | 0/44 |
| Sociología | 3/171 | 3/171 | 3/171 | 3/171 | 1/171 |
| Teatro | 0/27 | 7/27 | 7/27 | 7/27 | 6/27 |
| Trabajo social | 38/134 | 35/134 | 35/134 | 34/134 | 33/134 |

Para reproducir desde `backend/` con el CSV histórico de las 40 clases:

```bash
python3 -m scripts.compare_riasec_42 --baseline /ruta/al/csv-historico.csv
```
