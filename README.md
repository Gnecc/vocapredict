# VocaPredict

VocaPredict es un proyecto de clasificacion vocacional basado en puntajes de
intereses. El flujo principal del repositorio entrena un clasificador SVM con
un conjunto de datos normalizado, guarda los artefactos del modelo y los usa
para predecir una carrera desde:

- una interfaz de linea de comandos;
- una API HTTP construida con FastAPI;
- un contenedor listo para ejecutarse con Uvicorn.

## Flujo principal

1. `train.py` selecciona un modulo de entrenamiento desde `models/factory.py`.
2. `models/svmFinal.py` lee `conjunto_de_datos_normalizados.xlsx`, entrena el
   modelo SVM y genera `svm_model.joblib` y `label_encoder.joblib`.
3. `predict.py` carga esos artefactos para predecir una entrada de 9 puntajes.
4. `serve.py` expone la misma prediccion mediante `POST /predict`.

Los artefactos SVM ya estan incluidos en el repositorio, por lo que la
prediccion local y la API pueden ejecutarse sin volver a entrenar primero.

## Estructura

```text
.
|-- data/alumnos.csv                         # Dataset CSV de referencia
|-- conjunto_de_datos_normalizados.xlsx      # Dataset usado por los scripts de entrenamiento
|-- models/                                  # Scripts de modelos y factory
|-- train.py                                 # Entrada para entrenamiento
|-- predict.py                               # Prediccion desde consola
|-- serve.py                                 # API FastAPI
|-- svm_model.joblib                         # Modelo SVM persistido
|-- label_encoder.joblib                     # Encoder de etiquetas
|-- Dockerfile                               # Imagen para servir la API
|-- fly.toml                                 # Configuracion de despliegue en Fly.io
`-- requirements.txt                         # Dependencias declaradas
```

## Datos de entrada

Cada prediccion recibe 9 valores numericos normalizados en el mismo orden que
las variables del dataset:

1. `calculo`
2. `C. Fisico`
3. `C. Biologico`
4. `Mecanico`
5. `Servicio social`
6. `Literario`
7. `Persuasivo`
8. `Artistico`
9. `Musical`

La ultima columna del dataset corresponde a la etiqueta de carrera
(`Etiqueta` en `data/alumnos.csv` y `CARRERA_ACTUAL` en algunos scripts
historicos).

## Requisitos

- Python 3.12 o compatible.
- `pip` para instalar las dependencias declaradas.

## Instalacion local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Predecir desde consola

```bash
python3 -u predict.py \
  --scores "0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68"
```

`predict.py` valida que se reciban exactamente 9 valores y muestra:

- la clase predicha;
- el indice codificado de la clase;
- las probabilidades mas altas si el modelo cargado implementa
  `predict_proba`.

El numero de probabilidades impresas se puede ajustar con `--topk`:

```bash
python3 -u predict.py \
  --scores "0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68" \
  --topk 4
```

## Entrenar el SVM

```bash
python3 train.py --model svm
```

El entrenamiento vuelve a escribir:

- `svm_model.joblib`;
- `label_encoder.joblib`.

El script SVM tambien calcula metricas ROC/AUC multiclase y muestra una grafica
al finalizar.

## Servir la API

Inicia FastAPI con Uvicorn:

```bash
uvicorn serve:app --host 0.0.0.0 --port 8080
```

La API carga `svm_model.joblib` y `label_encoder.joblib` desde el directorio de
trabajo. La ruta disponible es:

```http
POST /predict
Content-Type: application/json
```

Ejemplo de request:

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"scores":[0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68]}'
```

Ejemplo de respuesta:

```json
{
  "prediction": "ICO",
  "index": 0,
  "probabilities": {
    "ICO": 0.83,
    "LIA": 0.09
  }
}
```

Las etiquetas y probabilidades concretas dependen de los artefactos cargados.

## Ejecutar con Docker

```bash
docker build -t vocapredict .
docker run --rm -p 8080:8080 vocapredict
```

La imagen copia el servicio FastAPI y los artefactos SVM persistidos. El
`Dockerfile` expone el puerto `8080`, que tambien coincide con la configuracion
de `fly.toml`.

## Modelos disponibles

`train.py` acepta estos valores para `--model`:

| Opcion | Modulo |
| --- | --- |
| `svm` | `models/svmFinal.py` |
| `knn` | `models/knnFinal.py` |
| `rf` | `models/randomForestFinal.py` |
| `kmeans` | `models/kmeansFinal.py` |
| `fcm` | `models/fuzzyFinal.py` |
| `pca` | `models/PCAFinal.py` |

El flujo integrado y persistido del repositorio es el de `svm`. Los demas
modulos conservan scripts exploratorios de modelado y visualizacion; algunos se
ejecutan al importarse, usan dependencias que no aparecen en
`requirements.txt` o incluyen sintaxis propia de notebooks. Conviene revisarlos
antes de usarlos como parte de un pipeline automatizado.

## Notas de desarrollo

- `serve.py` no reentrena el modelo: solo carga artefactos existentes.
- El orden de los 9 puntajes es parte del contrato de entrada del modelo.
- `requirements.txt` cubre el servicio y las dependencias base del flujo SVM;
  los scripts de analisis historico pueden requerir librerias adicionales para
  graficas, estadistica o clustering difuso.
