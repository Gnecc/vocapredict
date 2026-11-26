# Red semántica e inferencia exploratoria

Este módulo conserva el grafo NetworkX de cinco alumnos de ejemplo y permite
consultar los 1,400 perfiles del CSV con RDFLib y OWL-RL. Los perfiles CSV
contienen **intereses** normalizados, no mediciones de habilidad ni diagnósticos
vocacionales. Hay 350 registros originales y 1,050 sintéticos.

## Criterio y roles de Hereford

Tres roles de software cooperan de forma determinista en `criterio.py`:

1. **Análisis de intereses** (`AgenteIntereses`): toma las dos áreas con mayor
   puntaje, incluidas las empatadas en el segundo lugar, siempre que alcancen
   0.70. La situación socioeconómica queda fuera de esta selección.
2. **Vínculos con carreras** (`AgenteVinculos`): aporta relaciones de varios a
   varios entre áreas y carreras. Se derivaron de los perfiles objetivo de
   `backend/scripts/relabel_dataset.py`: se incluyó cada área con valor de
   referencia de al menos 0.70. Son relaciones provisionales.
3. **Revisión de evidencia** (`AgenteRevision`): marca una sola área de apoyo
   como *pista inicial* y dos o más como *convergencia de intereses*. Si ninguna
   área principal está vinculada, el sistema se abstiene de mostrar carrera.

Una combinación puede conectar con varias carreras. Se muestran todas,
ordenadas por número de áreas de apoyo; el orden no es una probabilidad ni una
recomendación. En este conjunto, 84 perfiles conectan con cuatro carreras y
289 quedan sin conexión. La cobertura no mide acierto, porque las etiquetas
del CSV también se generaron a partir de plantillas.

La regla OWL-RL se declara en `inferencia.py`:

```text
interesPrincipal + areaPerfilReferencia -> conexionExploratoria
```

Python selecciona las áreas por puntaje; OWL-RL deduce la conexión mediante
la cadena de propiedades. Cada resultado presenta las áreas y puntajes que
permiten reconstruir la deducción. La versión `intereses-referencia-v1` queda
registrada en el archivo OWL.

Los roles son componentes de software. La interpretación profesional de estas
relaciones, su pertinencia curricular y su validez para orientación vocacional
requieren revisión por personas especialistas. El sistema no predice éxito,
empleabilidad ni satisfacción. La etiqueta `CARRERA_ACTUAL` del CSV se generó
con plantillas históricas y no interviene en la regla; AMAI tampoco interviene.

## Ejecutar

Desde la raíz del proyecto:

```bash
backend/.venv/bin/python backend/red_semantica/main.py
```

La opción **13** explora los cinco alumnos de ejemplo, cuyos puntajes son
aleatorios. La opción **14** pide una fila del CSV. Por ejemplo, el perfil 7
muestra ICO e ISC con Cálculo y Mecánico como dos áreas de apoyo.

Para generar la ontología de los 1,400 perfiles y consultar una fila:

```bash
backend/.venv/bin/python backend/red_semantica/poblar_ontologia.py --perfil 7
```

El comando crea `backend/artifacts/perfiles_vocacionales.owl` en RDF/XML y
vuelve a abrirlo para ejecutar OWL-RL sobre el perfil solicitado. El CSV se
verifica contra `procedencia_perfiles.csv`, que contiene origen, fila fuente y
firma SHA-256. Cada perfil conserva sus nueve evaluaciones, su origen y su
etiqueta generada. La expansión OWL-RL se hace sobre un perfil por consulta.
Si cambia el criterio o el catálogo, hay que volver a ejecutar el importador:
las áreas principales quedan materializadas en el archivo OWL.

## Verificar

```bash
backend/.venv/bin/python -m unittest discover -s backend/red_semantica -p 'test_*.py'
```
## Catálogo e inferencia RIASEC

El catálogo RDF incluye las 42 opciones del experimento RIASEC. La inferencia
usa 13 perfiles provisionales de [Zenodo](https://doi.org/10.5281/zenodo.21403867),
con su código de tres letras, programa de origen y DOI. Las demás opciones
se pueden consultar por nombre. El catálogo y la inferencia se ejecutan por
separado de la API de predicción.

Los seis puntajes van de 0.2 a 1 en orden R, I, A, S, E, C. Se toman las áreas
con puntaje superior al cuarto lugar, con un máximo de tres áreas destacadas.
OWL-RL obtiene opciones candidatas que comparten un área. La consulta muestra
solo las que comparten al menos dos y explica cuáles coincidieron. Los empates
en el corte pueden reducir la evidencia y dar lugar a una abstención.

### Comunicación y Periodismo

El perfil de Zenodo es **AES**. El [plan de FES Aragón](https://www.aragon.unam.mx/fes-aragon/public_html/documents/licenciaturas/comunicacion-y-periodismo/plan-de-estudios-comunicacion-y-periodismo.pdf)
aporta evidencia de expresión y producción de medios, persuasión y relaciones
públicas, e interacción con personas y públicos. Las materias de métodos de
investigación y reportaje también respaldan el interés investigador. El plan
permite una correspondencia parcial, sin establecer el orden AES. El programa,
el código y la revisión son consultables en el OWL. La consulta habitual usa
los 13 perfiles iniciales. Para habilitar Comunicación y Periodismo en una
consulta experimental, usa `--cpe-experimental` con `AES` o una variante
que incluya Investigación. La [comparación](../docs/comunicacion_periodismo_owl.md)
seleccionó `AEI` entre las variantes.

```bash
backend/.venv/bin/python backend/red_semantica/riasec_owl.py --cpe-experimental AEI --puntajes 0.8 0.95 0.9 0.3 0.4 0.2
```

### Ejecutar desde la raíz

```bash
backend/.venv/bin/python -m pip install -r backend/red_semantica/requirements.txt
backend/.venv/bin/python backend/red_semantica/riasec_owl.py --catalogo
backend/.venv/bin/python backend/red_semantica/riasec_owl.py --puntajes 0.6 0.95 0.3 0.4 0.5 0.9 --salida backend/artifacts/ontologia_riasec.owl
backend/.venv/bin/python -m unittest discover -s backend/red_semantica -p 'test_riasec_owl.py'
```

La opción **11** de `main.py` también permite ingresar los seis
puntajes. Con solo `--salida`, el archivo RDF/XML contiene el catálogo sin
los datos de una consulta.


La opción **12** consulta el CSV unificado por `source_row_id` de OpenPsychometrics.
Usa los seis puntajes RIASEC del perfil elegible y aplica el mismo criterio OWL-RL
que la opción 11. El resultado puede quedar vacío cuando las áreas destacadas no
aportan dos coincidencias con ninguna referencia disponible.

```bash
backend/.venv/bin/python backend/red_semantica/riasec_owl.py --perfil-riasec ID
```

La opción **15** abre el grafo de demostración de Hereford.

## Catálogo ampliado de evaluación

La opción **2** muestra las 42 referencias del ensayo. Incluye 13 códigos de
Zenodo, 28 códigos calculados con el promedio de los perfiles de entrenamiento
del CSV y el código **AEI experimental** de Comunicación y Periodismo.
El predictor web usa el catálogo habitual de 13 referencias.

Para probar la inferencia ampliada por consola, añade `--catalogo-ampliado`:

```bash
backend/.venv/bin/python backend/red_semantica/riasec_owl.py \
  --catalogo-ampliado --puntajes 0.6 1 0.2 0.4 0.4 0.8
```

Desde `backend/`, los siguientes comandos regeneran las referencias y el
[informe](../docs/referencias_ampliadas_riasec.md):

```bash
git show e953434:backend/data/vocapredict_unificado_riasec.csv > /tmp/vocapredict-riasec40-base.csv
.venv/bin/python -m scripts.ampliar_referencias_riasec --baseline /tmp/vocapredict-riasec40-base.csv
```
