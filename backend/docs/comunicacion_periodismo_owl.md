# Comunicación y Periodismo con Investigación en la ontología RIASEC

Se compara AES, código de Zenodo, con tres variantes que sustituyen una letra
por I (Investigador). Las variantes son hipótesis del proyecto basadas en
las asignaturas de métodos y reportaje de FES Aragón. El orden de las letras
se conserva para lectura. La regla actual usa el conjunto de letras.

[Catálogo Zenodo](https://doi.org/10.5281/zenodo.21403867) · [Plan de FES Aragón](https://www.aragon.unam.mx/fes-aragon/public_html/documents/licenciaturas/comunicacion-y-periodismo/plan-de-estudios-comunicacion-y-periodismo.pdf)

Se elige la variante por F1 en los 33,417 casos de entrenamiento.
La comparación final usa los 8,355 perfiles de prueba previos,
incluidos 219 con Comunicación y 72 con Periodismo declarado. Las demás carreras
sirven para medir cuántas veces se muestra la conexión fuera del grupo. Esto evalúa
coincidencia con una carrera declarada en una muestra internacional. La partición
ya se usó en experimentos previos.

La comparación masiva aplica el mismo criterio de la consulta OWL. Usa las áreas
por encima del cuarto lugar y exige dos coincidencias. La prueba individual
comprueba que OWL-RL deduzca la candidatura y que se devuelva la evidencia.

## Selección en entrenamiento

| Código | Conexiones | Comunicación | Periodismo | Otras carreras | Precisión | Recobrado | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| AES | 22,877 | 764/873 | 231/288 | 21882/32256 | 4.3% | 85.7% | 8.3% |
| AEI | 20,312 | 643/873 | 219/288 | 19450/32256 | 4.2% | 74.2% | 8.0% |
| AIS | 25,681 | 736/873 | 254/288 | 24691/32256 | 3.9% | 85.3% | 7.4% |
| IES | 25,456 | 687/873 | 220/288 | 24549/32256 | 3.6% | 78.1% | 6.8% |

Variante elegida **AEI**.

## Comparación en prueba

| Código | Conexiones | Comunicación | Periodismo | Otras carreras | Precisión | Recobrado | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| AES | 5,730 | 192/219 | 68/72 | 5470/8064 | 4.5% | 89.3% | 8.6% |
| AEI | 5,078 | 160/219 | 57/72 | 4861/8064 | 4.3% | 74.6% | 8.1% |

Desde `backend/`, con el CSV histórico de 40 carreras:

```bash
python3 -m scripts.compare_cpe_owl --baseline /ruta/al/csv-historico.csv
```
