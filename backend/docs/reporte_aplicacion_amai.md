# Aplicacion de la clasificacion AMAI

## Objetivo

El archivo socioeconomico fue complementado con una clasificacion que resume
las condiciones del hogar en un solo nivel. Tambien se agrego un valor entre
`0` y `1` para facilitar su uso posterior en modelos de aprendizaje automatico.

## Version utilizada

Se utilizo la **Regla de Nivel Socioeconomico AMAI 2024**, publicada por la
Asociacion Mexicana de Agencias de Inteligencia de Mercado y Opinion (AMAI).
Esta version mantiene el cuestionario y los puntajes de la Regla AMAI 2022,
despues de su revision con los datos nacionales de la ENIGH 2022.

Fuentes oficiales:

- https://www.amai.org/NSE/index.php?queVeo=NSE2024
- https://www.amai.org/descargas/CUESTIONARIO_AMAI_2022.pdf

## Como se aplico

Para cada registro se consideraron seis datos del hogar:

1. Escolaridad del jefe o jefa del hogar.
2. Numero de baños completos.
3. Numero de automoviles o camionetas.
4. Disponibilidad de internet fijo en el hogar.
5. Numero de personas de 14 años o mas que trabajaron el ultimo mes.
6. Numero de cuartos utilizados para dormir.

Cada respuesta aporta una cantidad de puntos definida por AMAI. Los puntos se
suman y el resultado se ubica en uno de siete niveles:

| Nivel | Puntaje AMAI | Interpretacion general |
| --- | ---: | --- |
| A/B | 202 o mas | Hogares con las condiciones socioeconomicas mas favorables. |
| C+ | 168 a 201 | Hogares con condiciones altas y buena disponibilidad de recursos. |
| C | 141 a 167 | Hogares con condiciones medias y recursos relativamente estables. |
| C- | 116 a 140 | Hogares de nivel medio bajo, con algunas limitaciones. |
| D+ | 95 a 115 | Hogares con recursos limitados y cobertura parcial de necesidades. |
| D | 48 a 94 | Hogares con condiciones economicas bajas y mayores limitaciones. |
| E | 0 a 47 | Hogares con las condiciones socioeconomicas mas limitadas. |

Estas descripciones son orientativas. La letra resume caracteristicas del hogar
y no debe interpretarse como una evaluacion del valor, capacidad o potencial de
las personas.

## Normalizacion de 0 a 1

El puntaje maximo posible de la regla es `300`. Para obtener el valor
normalizado se aplico:

`valor_amai_normalizado = puntaje_amai / 300`

Por lo tanto:

- Un valor cercano a `0` representa condiciones socioeconomicas mas limitadas.
- Un valor cercano a `1` representa condiciones socioeconomicas mas favorables.
- Los valores intermedios conservan las diferencias de puntaje entre hogares,
  incluso cuando pertenecen a la misma categoria por letra.

Este valor continuo es util para modelos de prediccion, mientras que la
clasificacion por letra es mas sencilla para reportes y comparaciones.

## Columnas agregadas

- `nivel_socioeconomico_amai`: clasificacion por letra.
- `valor_amai_normalizado`: valor continuo entre `0` y `1`.

La columna `origen_registro` se conserva para distinguir los registros reales
de los sinteticos.
