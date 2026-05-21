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
2. `models/svmFinal.py` lee por defecto `conjunto_de_datos_reetiquetados.xlsx`,
   separa un holdout real y aumenta solo el fold de entrenamiento.
3. `predict.py` carga esos artefactos para predecir una entrada de 9 puntajes.
4. `serve.py` expone la misma prediccion mediante `POST /predict`.

Los artefactos SVM ya estan incluidos en el repositorio, por lo que la
prediccion local y la API pueden ejecutarse sin volver a entrenar primero.

En uso normal la API **no entrena al iniciar**. `serve.py` carga el modelo SVM
persistido en `svm_model.joblib` y su encoder en `label_encoder.joblib`.
Solo hace falta reentrenar cuando se quiera actualizar esos artefactos con un
dataset, etiquetas o configuracion de modelo nuevos.

## Estructura

```text
.
|-- data/alumnos.csv                         # Dataset CSV de referencia
|-- conjunto_de_datos_normalizados.xlsx      # Dataset original de referencia
|-- conjunto_de_datos_reetiquetados.xlsx     # Dataset real usado por entrenamiento
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

## Entrenar modelos

```bash
python3 train.py --model svm
```

El entrenamiento supervisado de `svm`, `knn` y `rf` usa por defecto el dataset
real reetiquetado, genera datos sinteticos solo para el fold de entrenamiento y
evalua contra un holdout real. Para usar otro dataset:

```bash
python3 train.py --model rf --dataset ruta/al/dataset.xlsx
```

El entrenamiento SVM vuelve a escribir:

- `svm_model.joblib`;
- `label_encoder.joblib`.

Las metricas y artefactos adicionales de los modelos se guardan en
`artifacts/`.

Despues de entrenar `svm`, la API y `predict.py` usaran los nuevos artefactos
guardados en la raiz del proyecto en su siguiente arranque o ejecucion.

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

El flujo integrado para prediccion de la API sigue siendo el de `svm`. `knn` y
`rf` tambien guardan modelos supervisados en `artifacts/`; `kmeans`, `fcm` y
`pca` quedan como rutas exploratorias de clustering o reduccion de dimension.

## Notas de desarrollo

- `serve.py` no reentrena el modelo: solo carga artefactos existentes.
- Para servir la API basta con que existan `svm_model.joblib` y
  `label_encoder.joblib`.
- El orden de los 9 puntajes es parte del contrato de entrada del modelo.
- `requirements.txt` cubre el servicio y los flujos de entrenamiento actuales.
