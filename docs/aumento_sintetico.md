# Aumento sintetico del dataset

Este documento resume el aumento aplicado al conjunto reetiquetado de
VocaPredict.

## Objetivo

Crear un dataset balanceado con `350` registros por clase y mantener una
proporcion final de `75%` de datos sinteticos.

## Entrada

Se uso:

- `data/conjunto_de_datos_reetiquetados.csv`

Conteo inicial:

| Clase | Registros reales |
| --- | ---: |
| `ICO` | 119 |
| `ISC` | 85 |
| `LIA` | 52 |
| `LLE` | 94 |

## Metodo

El script `scripts/augment_dataset.py` genera muestras sinteticas por
interpolacion dentro de la misma clase:

1. selecciona una fila real de una clase;
2. elige uno de sus vecinos cercanos de esa misma clase;
3. crea un nuevo punto entre ambos usando un factor aleatorio.

Este enfoque evita duplicar filas exactas y conserva la escala numerica de las
9 preferencias.

## Resultado

| Dato | Cantidad |
| --- | ---: |
| Registros reales | 350 |
| Registros sinteticos | 1050 |
| Registros finales | 1400 |
| Registros por clase | 350 |

Archivos generados:

- `data/conjunto_de_datos_aumentado_75_sintetico.csv`
- `conjunto_de_datos_aumentado_75_sintetico.xlsx`
- `data/auditoria_aumento_75_sintetico.csv`
- `data/resumen_aumento_75_sintetico.json`

La auditoria indica para cada muestra si es real o sintetica y, para los datos
sinteticos, que filas se usaron para crearla.

## Nota de uso

El dataset aumentado es util para entrenamiento. Para evaluar un modelo de forma
confiable, la particion de prueba debe mantenerse con datos reales y el aumento
sintetico debe aplicarse solo al conjunto de entrenamiento.
