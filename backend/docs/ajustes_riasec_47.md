# Ajustes del predictor RIASEC de 47 carreras

La selección usó tres pliegues estratificados dentro del entrenamiento.
Se eligió por el promedio del top 3 de las 47 carreras. La variante equilibrada
también limita a tres puntos porcentuales la caída del top 3 global de las
carreras compartidas durante la validación interna. El umbral es una decisión
para explorar el compromiso entre cobertura y aciertos globales.
Se conservaron los 8,083 casos compartidos y los 385 nuevos de la prueba anterior.
La prueba ya se había descrito en el informe anterior y sigue siendo exploratoria.

Para reproducir desde `backend/` con el CSV histórico de 40 clases:

```bash
python3 -m scripts.tune_riasec --baseline /ruta/al/csv-historico.csv
```

## Validación interna

| Configuración | Top 3 compartidas | Top 3 promedio por carrera | Carreras en cero |
|---|---:|---:|---:|
| 47 original | 46.0% | 19.1% | 9 |
| Logística grado 1, peso 0.4 | 49.3% | 17.3% | 12 |
| Logística grado 2, peso 0.4 | 48.9% | 17.8% | 5 |
| Discriminante cuadrático, peso 0.4 | 48.8% | 10.6% | 32 |
| Logística grado 1, peso 0.6 | 46.0% | 19.1% | 9 |
| Logística grado 2, peso 0.6 | 44.7% | 19.5% | 3 |
| Discriminante cuadrático, peso 0.6 | 49.6% | 11.7% | 25 |
| Logística grado 1, peso 0.8 | 37.4% | 21.0% | 1 |
| Logística grado 2, peso 0.8 | 34.5% | 20.9% | 1 |
| Discriminante cuadrático, peso 0.8 | 49.8% | 14.9% | 15 |
| Logística grado 1, peso 1 | 20.3% | 21.7% | 0 |
| Logística grado 2, peso 1 | 18.4% | 21.5% | 0 |
| Discriminante cuadrático, peso 1 | 14.8% | 20.3% | 1 |

- **47 equilibrado** usa Logística grado 2, peso 0.6.
- **47 énfasis por carrera** usa Logística grado 1, peso 1.

## Misma partición de prueba

| Modelo | Grupo | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Carreras en cero |
|---|---|---:|---:|---:|---:|---:|
| 40 original | compartidas | 8083 | 28.5% | 47.1% | 21.3% | 7 |
| 40 original | nuevas | 385 | 0.0% | 0.0% | 0.0% | 7 |
| 40 original | todas | 8468 | 27.2% | 45.0% | 18.2% | 14 |
| 47 original | compartidas | 8083 | 27.9% | 45.9% | 20.0% | 8 |
| 47 original | nuevas | 385 | 4.4% | 20.8% | 12.8% | 3 |
| 47 original | todas | 8468 | 26.8% | 44.8% | 19.0% | 11 |
| 47 equilibrado | compartidas | 8083 | 27.0% | 44.9% | 20.4% | 5 |
| 47 equilibrado | nuevas | 385 | 5.2% | 19.0% | 11.8% | 2 |
| 47 equilibrado | todas | 8468 | 26.0% | 43.7% | 19.1% | 7 |
| 47 énfasis por carrera | compartidas | 8083 | 7.8% | 20.3% | 19.8% | 0 |
| 47 énfasis por carrera | nuevas | 385 | 8.3% | 25.2% | 34.2% | 0 |
| 47 énfasis por carrera | todas | 8468 | 7.8% | 20.6% | 21.9% | 0 |

## Top 3 por carrera

Cada celda muestra aciertos sobre el número de casos de prueba.
El modelo de 40 carece de las siete clases nuevas.

| Carrera | 40 original | 47 original | 47 equilibrado | 47 énfasis por carrera |
|---|---:|---:|---:|---:|
| Administración Hotelera | — | 0/22 | 0/22 | 11/22 |
| Administración de empresas | 156/297 | 150/297 | 138/297 | 96/297 |
| Antropología | 5/59 | 6/59 | 4/59 | 12/59 |
| Arquitectura | 24/102 | 20/102 | 30/102 | 22/102 |
| Biología | 289/404 | 289/404 | 286/404 | 190/404 |
| Bioquímica | 7/51 | 7/51 | 10/51 | 16/51 |
| Ciencias Ambientales | — | 0/39 | 1/39 | 2/39 |
| Ciencias de la computación | 68/240 | 67/240 | 64/240 | 31/240 |
| Ciencias políticas | 1/131 | 1/131 | 0/131 | 1/131 |
| Cinematografía | — | 8/26 | 5/26 | 15/26 |
| Comunicación | — | 64/219 | 58/219 | 39/219 |
| Contaduría | 154/280 | 152/280 | 137/280 | 126/280 |
| Criminología | 0/35 | 0/35 | 0/35 | 2/35 |
| Derecho | 34/209 | 20/209 | 16/209 | 9/209 |
| Diseño gráfico | 6/52 | 2/52 | 5/52 | 9/52 |
| Economía | 17/208 | 14/208 | 15/208 | 8/208 |
| Educación | 150/357 | 139/357 | 123/357 | 49/357 |
| Educación Primaria | — | 1/29 | 0/29 | 12/29 |
| Enfermería | 233/439 | 232/439 | 226/439 | 158/439 |
| Farmacia | 1/46 | 1/46 | 1/46 | 8/46 |
| Filosofía | 12/83 | 10/83 | 11/83 | 9/83 |
| Finanzas | 31/147 | 30/147 | 34/147 | 35/147 |
| Física | 18/90 | 18/90 | 19/90 | 22/90 |
| Geografía | 0/42 | 0/42 | 0/42 | 2/42 |
| Historia | 17/185 | 16/185 | 9/185 | 3/185 |
| Historia del Arte | — | 0/23 | 2/23 | 1/23 |
| Ingeniería civil | 94/205 | 94/205 | 103/205 | 71/205 |
| Ingeniería de software | 0/24 | 0/24 | 1/24 | 5/24 |
| Ingeniería eléctrica | 20/93 | 20/93 | 16/93 | 29/93 |
| Ingeniería en computación | 0/57 | 0/57 | 3/57 | 3/57 |
| Ingeniería industrial | 0/23 | 0/23 | 0/23 | 1/23 |
| Ingeniería mecánica | 72/144 | 74/144 | 70/144 | 69/144 |
| Ingeniería química | 4/81 | 5/81 | 2/81 | 14/81 |
| Justicia penal | 22/175 | 20/175 | 24/175 | 25/175 |
| Kinesiología | 6/53 | 6/53 | 4/53 | 16/53 |
| Lingüística | 0/39 | 0/39 | 1/39 | 4/39 |
| Matemáticas | 22/157 | 22/157 | 18/157 | 18/157 |
| Medicina | 21/150 | 21/150 | 28/150 | 26/150 |
| Mercadotecnia | 54/174 | 44/174 | 46/174 | 42/174 |
| Música | 51/92 | 48/92 | 45/92 | 49/92 |
| Periodismo | 10/72 | 0/72 | 5/72 | 8/72 |
| Psicología | 2150/2629 | 2127/2629 | 2070/2629 | 377/2629 |
| Química | 17/109 | 17/109 | 20/109 | 22/109 |
| Relaciones internacionales | 0/44 | 0/44 | 0/44 | 5/44 |
| Sociología | 3/171 | 3/171 | 12/171 | 8/171 |
| Teatro | — | 7/27 | 7/27 | 17/27 |
| Trabajo social | 38/134 | 36/134 | 33/134 | 44/134 |
