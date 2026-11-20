# Red semántica e inferencia exploratoria

Este módulo conserva el grafo NetworkX de cinco alumnos de ejemplo y permite
consultar los 1,400 perfiles del CSV con RDFLib y OWL-RL. Los perfiles CSV
contienen **intereses** normalizados, no mediciones de habilidad ni diagnósticos
vocacionales. Hay 350 registros originales y 1,050 sintéticos.

## Criterio y roles

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
backend/.venv/bin/python backend/red_semantica/red_semantica.py
```

La opción **9** explora los cinco alumnos de ejemplo, cuyos puntajes son
aleatorios. La opción **10** pide una fila del CSV. Por ejemplo, el perfil 7
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
