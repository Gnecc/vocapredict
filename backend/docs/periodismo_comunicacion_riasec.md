# Periodismo y Comunicación en el predictor RIASEC

Se reutilizaron los 8,083 casos compartidos y los 272 nuevos
del experimento 40 vs. 43. Entre los 72 casos declarados de Periodismo,
Comunicación apareció en el top 3 del modelo de 43 en 22.
Apareció en 5 de los 10 casos que
el modelo de 40 acertaba y el de 43 dejó de acertar.

| Diagnóstico sobre Periodismo | Aciertos top 3 |
|---|---:|
| Modelo de 40 | 10/72 |
| Modelo de 43 | 0/72 |
| Modelo de 43 ocultando Comunicación al ordenar | 4/72 |
| Reentrenamiento de 42 sin Comunicación | 4/72 |

## Ajuste de peso

Se escogió el multiplicador con más aciertos en Periodismo en tres pliegues
estratificados dentro del entrenamiento. Se permitió perder hasta un punto
porcentual en las carreras compartidas y hasta tres en Comunicación frente
al de 43 sin ajuste, medidos durante la validación interna. Los empates
favorecen el multiplicador menor. La partición de prueba ya era conocida de
experimentos anteriores, por lo que los resultados son exploratorios.

| Peso de Periodismo | Top 3 Periodismo | Top 3 Comunicación | Top 3 compartidas | Cumple límites |
|---:|---:|---:|---:|---|
| 1 | 2.1% | 30.8% | 46.2% | Sí |
| 1.15 | 5.2% | 30.1% | 46.1% | Sí |
| 1.3 | 10.8% | 28.9% | 46.1% | Sí |
| 1.5 | 21.2% | 27.3% | 45.9% | No |
| 1.75 | 32.6% | 25.5% | 45.7% | No |
| 2 | 41.0% | 24.3% | 45.5% | No |
| 2.5 | 51.4% | 22.3% | 45.1% | No |
| 3 | 63.2% | 21.1% | 44.8% | No |

Multiplicador elegido sobre el peso original de Periodismo **1.3×**.

## Evaluación en la misma prueba

La precisión de Periodismo es la proporción de recomendaciones en las que
Periodismo aparece en el top 3 y coincide con la carrera declarada.

| Modelo | Top 3 Periodismo | Precisión de Periodismo | Top 3 Comunicación | Top 3 compartidas | Top 3 nuevas | Top 3 total |
|---|---:|---:|---:|---:|---:|---:|
| 40 original | 10/72 | 10/258 | — | 47.1% | 0.0% | 45.6% |
| 43 original | 0/72 | 0/33 | 65/219 | 45.8% | 29.4% | 45.3% |
| 43 ajustado | 8/72 | 8/382 | 62/219 | 45.8% | 28.3% | 45.3% |

Para reproducir desde `backend/` con el mismo CSV de las 40 clases:

```bash
python3 -m scripts.check_riasec_journalism --baseline /ruta/al/csv-historico.csv
```
