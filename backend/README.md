# VocaPredict

VocaPredict es un proyecto de clasificacion vocacional basado en puntajes de
intereses y un indicador socioeconomico AMAI normalizado. El flujo principal
del repositorio entrena un clasificador SVM con un conjunto de datos aumentado,
guarda los artefactos del modelo y los usa para predecir una carrera desde:

- una interfaz de linea de comandos;
- una API HTTP construida con FastAPI;
- un contenedor listo para ejecutarse con Uvicorn.

## Flujo principal

1. `train.py` selecciona un modulo de entrenamiento desde `models/factory.py`.
2. `models/svmFinal.py` lee por defecto
   `data/conjunto_de_datos_aumentado_75_sintetico_amai.csv` y separa un
   holdout estratificado para evaluacion.
3. `predict.py` carga esos artefactos para predecir una entrada de 10 valores.
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
|-- data/conjunto_de_datos_aumentado_75_sintetico_amai.csv
|                                             # Dataset aumentado usado por entrenamiento
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

Cada prediccion recibe 10 valores numericos normalizados en el mismo orden que
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
10. `valor_amai_normalizado`

La ultima columna del dataset corresponde a la etiqueta de carrera
(`Etiqueta` en `data/alumnos.csv` y `CARRERA_ACTUAL` en algunos scripts
historicos).

## Perfiles de reetiquetado

El dataset reetiquetado se construyo comparando cada usuario contra estos
perfiles objetivo. Cada valor representa el nivel esperado de preferencia para
esa area en una escala normalizada.

| Area | `ICO` | `ISC` | `LIA` | `LLE` |
| --- | ---: | ---: | ---: | ---: |
| `calculo` | 0.90 | 0.90 | 0.65 | 0.25 |
| `C. Fisico` | 0.80 | 0.90 | 0.35 | 0.25 |
| `C. Biologico` | 0.25 | 0.25 | 0.25 | 0.25 |
| `Mecanico` | 0.90 | 0.70 | 0.35 | 0.25 |
| `Servicio social` | 0.35 | 0.50 | 0.75 | 0.75 |
| `Literario` | 0.35 | 0.45 | 0.55 | 0.95 |
| `Persuasivo` | 0.45 | 0.55 | 0.90 | 0.75 |
| `Artistico` | 0.30 | 0.35 | 0.45 | 0.65 |
| `Musical` | 0.25 | 0.25 | 0.30 | 0.40 |

La reetiqueta asigna la carrera cuyo perfil queda mas cerca de los 9 puntajes
del usuario. En esta version todas las areas participan con el mismo peso.
El valor AMAI se agrega despues como una variable adicional para el
entrenamiento predictivo.

## Requisitos

- Python 3.12 o compatible.
- `pip` para instalar las dependencias declaradas.

## Instalacion local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Predecir desde consola

```bash
python3 -u predict.py \
  --scores "0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68,0.45"
```

`predict.py` valida que se reciban los valores esperados por el modelo cargado
y muestra:

- la clase predicha;
- el indice codificado de la clase;
- las probabilidades mas altas si el modelo cargado implementa
  `predict_proba`.

El numero de probabilidades impresas se puede ajustar con `--topk`:

```bash
python3 -u predict.py \
  --scores "0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68,0.45" \
  --topk 4
```

## Entrenar modelos

```bash
python3 train.py --model svm
```

El entrenamiento supervisado de `svm`, `knn` y `rf` usa por defecto el dataset
aumentado con la variable `valor_amai_normalizado` y evalua contra un holdout
estratificado. Para usar otro dataset:

```bash
python3 train.py --model rf --dataset ruta/al/dataset.xlsx
```

Si se quiere aplicar aumento sintetico adicional solo al split de
entrenamiento, se puede usar `--augment-train`.

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
  -d '{"scores":[0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68,0.45]}'
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
- El orden de los 10 valores es parte del contrato de entrada del modelo.
- `requirements.txt` cubre el servicio y los flujos de entrenamiento actuales.
