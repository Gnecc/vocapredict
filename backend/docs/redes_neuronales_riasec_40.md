# Redes neuronales RIASEC de 40 carreras

Prueba histórica de 8,083 casos. Se comparan las seis escalas, las 48
respuestas y ambas representaciones juntas. Las respuestas se verificaron
recalculando los seis puntajes. Se eligieron arquitectura, regularización y
época en los 6,466 casos de validación interna por primera opción,
con top 3 y exactitud equilibrada para desempatar. La red se reentrenó con
todos los casos de entrenamiento durante el número de épocas elegido.
La partición de prueba se reutiliza. Los resultados son exploratorios.

| Modelo | Entrada | Primera opción | Top 3 | Exactitud equilibrada |
|---|---|---:|---:|---:|
| Logística activa | 6 puntajes | 28.5% | 47.1% | 8.3% |
| Logística regularizada | 48 respuestas | 36.3% | 57.2% | 8.5% |
| Red neuronal MLP | 6 puntajes | 33.6% | 51.3% | 4.3% |
| Red neuronal MLP | 48 respuestas | 36.7% | 57.2% | 9.1% |
| Red neuronal MLP | 48 respuestas + 6 puntajes | 36.5% | 57.2% | 8.1% |

## Selección en validación

| Entrada | Capas ocultas | Regularización | Época | Primera opción | Top 3 | Exactitud equilibrada | Elegida |
|---|---|---:|---:|---:|---:|---:|---|
| 6 puntajes | (32,) | 0.01 | 7 | 33.7% | 51.4% | 4.2% | — |
| 6 puntajes | (64, 32) | 0.1 | 8 | 33.9% | 52.2% | 4.4% | — |
| 6 puntajes | (128, 64) | 1 | 17 | 34.0% | 51.9% | 4.4% | Sí |
| 48 respuestas | (32,) | 0.01 | 34 | 36.8% | 56.9% | 9.4% | Sí |
| 48 respuestas | (64, 32) | 0.1 | 11 | 36.7% | 56.9% | 8.4% | — |
| 48 respuestas | (128, 64) | 1 | 8 | 36.8% | 57.3% | 7.7% | — |
| 48 respuestas + 6 puntajes | (32,) | 0.01 | 39 | 36.7% | 57.2% | 9.5% | — |
| 48 respuestas + 6 puntajes | (64, 32) | 0.1 | 11 | 36.7% | 57.1% | 8.3% | — |
| 48 respuestas + 6 puntajes | (128, 64) | 1 | 19 | 37.0% | 57.8% | 8.1% | Sí |

Ejecutar desde `backend/` con el CSV histórico de 40 clases y el TSV original:

```bash
python3 -m scripts.compare_riasec_mlp --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv
```
