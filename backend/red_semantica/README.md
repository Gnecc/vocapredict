# Red Semántica

Aquí se desarrollará el módulo de red semántica para el proyecto.

## Objetivo
Representar conocimiento mediante grafos usando preguntas y relaciones.

## Tecnologías
- Python (NetworkX)

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
