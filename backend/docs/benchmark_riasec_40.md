# Benchmark RIASEC de 40 carreras

Se reutilizaron los 8,083 casos de prueba originales.
Las configuraciones se eligieron por exactitud en 6,466 casos
reservados del entrenamiento. En empate se usaron top 3 y exactitud equilibrada,
en ese orden. Los modelos usan los seis puntajes RIASEC. La carrera declarada
es el objetivo. El resultado es exploratorio porque la partición ya se conocía.

Las tres clases más frecuentes del entrenamiento obtienen 43.0% en top 3.
Hay 31 vectores de puntajes con etiquetas distintas (123 filas).
24 casos de prueba tienen un vector idéntico a alguno de entrenamiento.
Estas coincidencias no establecen un techo de exactitud en perfiles nuevos.

La MLP usa un presupuesto fijo de entrenamiento de hasta 120 iteraciones.

| Modelo | Configuración | Primera opción | Top 3 | Exactitud equilibrada | Top 3 por clase |
|---|---|---:|---:|---:|---:|
| Clase más frecuente | fija | 32.5% | — | 2.5% | — |
| Regresión logística activa | fija | 28.5% | 47.1% | 8.3% | 21.3% |
| Logística con interacciones | grado 2, peso 0 | 33.5% | 51.9% | 4.6% | 17.4% |
| Red neuronal MLP | capas (32,) | 33.6% | 51.7% | 4.7% | 17.3% |
| Logística con características RBF | gamma 0.05 | 33.6% | 51.8% | 4.7% | 17.1% |
| k-NN | 250 vecinos | 33.1% | 51.1% | 3.4% | 16.0% |
| Random Forest | hoja mínima 30 | 33.4% | 51.2% | 3.9% | 15.7% |
| Extra Trees | hoja mínima 10 | 33.4% | 51.5% | 3.6% | 16.0% |
| Boosting de histogramas | 35 iteraciones | 33.4% | 51.1% | 4.3% | 16.8% |
| Naive Bayes gaussiano | suavizado 0.1 | 33.2% | 50.6% | 4.3% | 15.5% |
| Discriminante cuadrático | regularización 0.01 | 33.3% | 51.4% | 3.8% | 15.8% |

## Las 48 respuestas como entrada

Los modelos de esta sección usan las mismas preguntas antes de promediarlas.
Se verificó la correspondencia con los seis puntajes de cada fila y se usó la
misma partición. Las configuraciones se fijaron antes de consultar la prueba.

| Modelo | Primera opción | Top 3 | Exactitud equilibrada |
|---|---:|---:|---:|
| Logística regularizada | 36.3% | 57.2% | 8.5% |
| Red neuronal MLP | 35.6% | 55.9% | 8.8% |

## Selección dentro del entrenamiento

| Familia | Configuración | Primera opción | Top 3 | Exactitud equilibrada | Elegida |
|---|---|---:|---:|---:|---|
| Logística con interacciones | grado 1, peso 0 | 33.7% | 51.9% | 4.6% | — |
| Logística con interacciones | grado 1, peso 0.3 | 33.3% | 52.0% | 6.4% | — |
| Logística con interacciones | grado 1, peso 0.6 | 29.3% | 48.4% | 8.5% | — |
| Logística con interacciones | grado 2, peso 0 | 33.8% | 52.3% | 4.8% | Sí |
| Logística con interacciones | grado 2, peso 0.3 | 33.0% | 51.5% | 6.5% | — |
| Logística con interacciones | grado 2, peso 0.6 | 28.1% | 47.2% | 8.7% | — |
| Logística con interacciones | grado 3, peso 0 | 33.3% | 51.6% | 4.7% | — |
| Logística con interacciones | grado 3, peso 0.3 | 32.0% | 50.8% | 6.4% | — |
| Logística con interacciones | grado 3, peso 0.6 | 26.1% | 45.1% | 8.4% | — |
| Red neuronal MLP | capas (32,) | 33.7% | 52.1% | 4.7% | Sí |
| Red neuronal MLP | capas (64, 32) | 33.5% | 52.1% | 4.6% | — |
| Red neuronal MLP | capas (128, 64) | 32.9% | 51.3% | 5.3% | — |
| Logística con características RBF | gamma 0.05 | 33.7% | 52.2% | 4.6% | Sí |
| Logística con características RBF | gamma 0.15 | 33.5% | 52.3% | 4.5% | — |
| Logística con características RBF | gamma 0.4 | 33.6% | 51.6% | 4.5% | — |
| k-NN | 25 vecinos | 32.0% | 46.6% | 4.4% | — |
| k-NN | 100 vecinos | 33.3% | 50.4% | 3.8% | — |
| k-NN | 250 vecinos | 33.3% | 51.1% | 3.4% | Sí |
| Random Forest | hoja mínima 10 | 33.4% | 51.2% | 4.1% | — |
| Random Forest | hoja mínima 30 | 33.6% | 51.4% | 3.9% | Sí |
| Random Forest | hoja mínima 80 | 33.5% | 51.2% | 3.6% | — |
| Extra Trees | hoja mínima 10 | 33.6% | 51.5% | 3.7% | Sí |
| Extra Trees | hoja mínima 30 | 33.2% | 51.4% | 3.2% | — |
| Extra Trees | hoja mínima 80 | 32.7% | 50.8% | 2.7% | — |
| Boosting de histogramas | 35 iteraciones | 33.4% | 51.3% | 4.3% | Sí |
| Boosting de histogramas | 60 iteraciones | 33.1% | 51.4% | 4.4% | — |
| Naive Bayes gaussiano | suavizado 0.001 | 32.7% | 50.7% | 4.5% | — |
| Naive Bayes gaussiano | suavizado 0.1 | 32.9% | 50.9% | 4.1% | Sí |
| Discriminante cuadrático | regularización 0.01 | 33.6% | 51.8% | 3.9% | Sí |
| Discriminante cuadrático | regularización 0.1 | 32.5% | 48.0% | 2.5% | — |
| Discriminante cuadrático | regularización 0.4 | 32.5% | 44.7% | 2.5% | — |

Desde `backend/`, con el CSV histórico de 40 carreras:

```bash
python3 -m scripts.benchmark_riasec_40 --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv
```
