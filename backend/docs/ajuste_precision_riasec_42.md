# Ajuste de precisión de Comunicación y Periodismo

La prueba reutiliza los 8,083 casos compartidos y los 272 nuevos.
En todos los modelos se mide la clase agrupada según la comparación anterior.
El ajuste multiplica solo la puntuación de esa clase antes de ordenar las opciones.
En tres pliegues internos se maximiza su precisión, conservando al menos
80.0% de sus aciertos originales como decisión del experimento.
El factor se eligió antes de ejecutar la evaluación de prueba, reutilizada
de experimentos previos. Esta evaluación sigue siendo exploratoria.

| Factor | Aciertos del grupo | Veces en top 3 | Precisión | Cumple el mínimo |
|---:|---:|---:|---:|---|
| 1 | 428 | 4933 | 8.7% | Sí |
| 0.95 | 393 | 4372 | 9.0% | Sí |
| 0.9 | 346 | 3792 | 9.1% | Sí |
| 0.85 | 312 | 3228 | 9.7% | No |
| 0.8 | 264 | 2612 | 10.1% | No |
| 0.75 | 217 | 2071 | 10.5% | No |
| 0.7 | 172 | 1578 | 10.9% | No |
| 0.6 | 89 | 761 | 11.7% | No |
| 0.5 | 34 | 208 | 16.3% | No |

Factor elegido **0.9×**.

## Resultado en la misma partición

| Modelo | Precisión del grupo | Periodismo original | Comunicación original | Top 3 compartidos | Top 3 fuera del grupo | Top 3 total |
|---|---:|---:|---:|---:|---:|---:|
| 40 original | 35/258 (13.6%) | 10/72 | 25/219 | 47.1% | 47.1% | 45.9% |
| 42 original | 119/1276 (9.3%) | 35/72 | 84/219 | 46.0% | 45.9% | 45.7% |
| 42 ajustado | 92/958 (9.6%) | 26/72 | 66/219 | 46.1% | 46.1% | 45.6% |

## Top 3 por clase

| Clase | 40 original | 42 original | 42 ajustado |
|---|---:|---:|---:|
| Administración de empresas | 156/297 | 147/297 | 150/297 |
| Antropología | 5/59 | 6/59 | 6/59 |
| Arquitectura | 24/102 | 22/102 | 22/102 |
| Biología | 289/404 | 289/404 | 289/404 |
| Bioquímica | 7/51 | 7/51 | 7/51 |
| Ciencias de la computación | 68/240 | 67/240 | 67/240 |
| Ciencias políticas | 1/131 | 1/131 | 1/131 |
| Cinematografía | 0/26 | 8/26 | 8/26 |
| Comunicación y Periodismo | 35/291 | 119/291 | 92/291 |
| Contaduría | 154/280 | 152/280 | 152/280 |
| Criminología | 0/35 | 0/35 | 0/35 |
| Derecho | 34/209 | 18/209 | 19/209 |
| Diseño gráfico | 6/52 | 2/52 | 2/52 |
| Economía | 17/208 | 13/208 | 13/208 |
| Educación | 150/357 | 138/357 | 140/357 |
| Enfermería | 233/439 | 231/439 | 231/439 |
| Farmacia | 1/46 | 1/46 | 1/46 |
| Filosofía | 12/83 | 9/83 | 10/83 |
| Finanzas | 31/147 | 30/147 | 30/147 |
| Física | 18/90 | 18/90 | 18/90 |
| Geografía | 0/42 | 0/42 | 0/42 |
| Historia | 17/185 | 13/185 | 16/185 |
| Ingeniería civil | 94/205 | 93/205 | 93/205 |
| Ingeniería de software | 0/24 | 0/24 | 0/24 |
| Ingeniería eléctrica | 20/93 | 20/93 | 20/93 |
| Ingeniería en computación | 0/57 | 0/57 | 0/57 |
| Ingeniería industrial | 0/23 | 0/23 | 0/23 |
| Ingeniería mecánica | 72/144 | 72/144 | 72/144 |
| Ingeniería química | 4/81 | 4/81 | 4/81 |
| Justicia penal | 22/175 | 20/175 | 20/175 |
| Kinesiología | 6/53 | 6/53 | 6/53 |
| Lingüística | 0/39 | 0/39 | 0/39 |
| Matemáticas | 22/157 | 22/157 | 22/157 |
| Medicina | 21/150 | 21/150 | 21/150 |
| Mercadotecnia | 54/174 | 43/174 | 44/174 |
| Música | 51/92 | 45/92 | 46/92 |
| Psicología | 2150/2629 | 2121/2629 | 2125/2629 |
| Química | 17/109 | 16/109 | 16/109 |
| Relaciones internacionales | 0/44 | 0/44 | 0/44 |
| Sociología | 3/171 | 3/171 | 3/171 |
| Teatro | 0/27 | 7/27 | 7/27 |
| Trabajo social | 38/134 | 34/134 | 35/134 |

Para reproducir desde `backend/` con el CSV histórico de las 40 clases:

```bash
python3 -m scripts.tune_riasec_42 --baseline /ruta/al/csv-historico.csv
```
