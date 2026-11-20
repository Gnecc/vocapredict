# VocaPredict: modelo RIASEC

La API usa seis puntajes de intereses RIASEC, en el orden **R, I, A, S, E, C**. Cada puntaje es la media de las ocho respuestas del área, dividida entre 5. Por eso cada entrada válida está entre 0.2 y 1.0. El modelo ofrece tres carreras ordenadas. Se entrenó para reconocer la **carrera universitaria declarada** por participantes de OpenPsychometrics; sus resultados no validan satisfacción futura ni garantizan que una carrera sea adecuada para una persona.

## Datos

`data/vocapredict_unificado_riasec.csv` conserva las filas Hereford/AMAI de VocaPredict y las filas RIASEC con su procedencia, tipo de etiqueta y marca de sintético. Solo entran al entrenamiento las filas de `source=openpsychometrics_riasec`, `instrument=RIASEC` y `riasec_eligible=1`. El modelo no usa AMAI ni rellena puntajes Hereford en filas RIASEC. Las reglas revisables para traducir `major` a códigos y nombres de carrera están en `data/riasec_career_catalog.json`.

## Entrenar y evaluar

Desde `backend/`:

```bash
python3 -m pip install -r requirements.txt
python3 train.py
```

`train.py` divide los casos elegibles en entrenamiento y prueba con un holdout estratificado de 20 % **antes de cualquier modelado**. Ajusta un escalador y una regresión logística solo sobre entrenamiento. Aplica pesos de clase moderados calculados exclusivamente del conjunto de entrenamiento para que carreras menos frecuentes puedan aparecer en las sugerencias. Guarda `riasec_model.joblib` para la API y `artifacts/riasec_metrics.json` con exactitud y top 3 sobre carrera declarada, métricas por carrera, cobertura de carreras en el top 3 y comparación por país cuando hay al menos 50 casos de prueba de ese país. No genera ejemplos sintéticos. Para un CSV alternativo: `python3 train.py --dataset ruta/al/dataset.csv`.

Los comandos históricos `python3 train.py --model svm` y otros modelos del repositorio siguen disponibles, pero sus artefactos no alimentan la API RIASEC.

## API y consola

```bash
uvicorn serve:app --host 0.0.0.0 --port 8080
python3 predict.py --scores "0.8,0.9,0.5,0.6,0.4,0.5"
```

`POST /predict` acepta:

```json
{"scores": [0.8, 0.9, 0.5, 0.6, 0.4, 0.5]}
```

Devuelve `prediction` (código de la primera carrera), `recommendations` (hasta tres objetos con `career_code`, `career_name`, `score`), `probabilities` (todos los códigos; nombre conservado para compatibilidad), `career_labels` y una explicación de la procedencia del modelo. Debido a los pesos de clase, `score` es una **puntuación relativa del modelo**, no una probabilidad calibrada de estudiar esa carrera ni de éxito vocacional. Entradas con longitud o rango incorrecto reciben HTTP 422.

La imagen de Docker copia el artefacto `riasec_model.joblib` ya entrenado. Debe generarse antes de construir la imagen.
