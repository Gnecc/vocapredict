import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = '/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict';
const skill = '/Users/cisnerosbe/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
const build = path.join(root, '.codex_tmp/riasec_deck_20261015');
const output = path.join(root, 'outputs/VocaPredict_RIASEC_resumen_bn_v2.pptx');
const runtimePython = '/Users/cisnerosbe/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const report = path.join(root, 'backend/docs/reporte_riasec.md');
const summary = path.join(root, 'backend/data/riasec_preparation_summary.json');
const metrics = path.join(root, 'backend/artifacts/riasec_metrics.json');

const ppt = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const font = 'Arial';
const ink = '#000000';
const white = '#FFFFFF';

function slide() {
  const s = ppt.slides.add();
  s.background.fill = white;
  return s;
}

function text(s, value, left, top, width, height, size, bold = false) {
  const shape = s.shapes.add({
    geometry: 'textbox',
    position: { left, top, width, height },
    fill: 'none',
    line: { style: 'solid', fill: 'none', width: 0 },
  });
  shape.text = value;
  shape.text.style = { fontFamily: font, fontSize: size, bold, color: ink };
  return shape;
}

function title(s, value) {
  text(s, value, 76, 56, 1125, 70, 36, true);
}

function note(s, value) {
  text(s, value, 78, 630, 1120, 58, 19, false);
}

function table(s, values, top, height, widths, fontSize = 21) {
  const t = s.tables.add({
    rows: values.length,
    columns: values[0].length,
    left: 78,
    top,
    width: 1124,
    height,
    columnWidths: widths,
    values,
  });
  t.styleOptions = { headerRow: false, bandedRows: false, bandedColumns: false };
  t.borders.assign({ style: 'solid', fill: ink, width: 1 });
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[0].length; c++) {
      const cell = t.getCell(r, c);
      cell.fill = white;
      cell.text.style = { fontFamily: font, fontSize, color: ink, bold: r === 0 };
    }
  }
  return t;
}

// 1. Cover
{
  const s = slide();
  text(s, 'VocaPredict', 80, 188, 1100, 95, 58, true);
  text(s, 'Ampliación de carreras con RIASEC', 82, 302, 1080, 70, 34, false);
  text(s, 'Resumen de datos, modelo y límites', 84, 408, 1050, 50, 23, false);
  s.speakerNotes.text = `Fuente: ${report}`;
}

// 2. Two instruments, one auditable file
{
  const s = slide();
  title(s, 'Dos instrumentos en un archivo');
  table(s, [
    ['Origen', 'Filas', 'Intereses', 'Tipo de etiqueta'],
    ['VocaPredict', '1.400', '9 áreas Hereford + AMAI', 'Generada'],
    ['OpenPsychometrics', '145.828', '48 actividades RIASEC', 'Carrera declarada'],
  ], 176, 275, [260, 150, 400, 314], 21);
  note(s, 'Los campos no medidos quedan vacíos. No se inventaron equivalencias entre cuestionarios.');
  s.speakerNotes.text = `Fuentes: ${report}; ${summary}; https://openpsychometrics.org/_rawdata/`;
}

// 3. Data preparation
{
  const s = slide();
  title(s, 'Filtrado de respuestas RIASEC');
  table(s, [
    ['Paso', 'Filas restantes'],
    ['Respuestas originales', '145.828'],
    ['48 intereses válidos', '135.764'],
    ['Edad válida', '135.687'],
    ['Carrera clara y al menos 100 casos', '40.413'],
  ], 156, 386, [760, 364], 22);
  note(s, 'El catálogo acepta nombres explícitos; excluye respuestas vacías o ambiguas.');
  s.speakerNotes.text = `Fuentes: ${report}; ${summary}. Las razones de exclusión son sucesivas.`;
}

// 4. New recommendation flow
{
  const s = slide();
  title(s, 'Nuevo flujo de VocaPredict');
  table(s, [
    ['Etapa', 'Qué hace la aplicación'],
    ['1. Cuestionario', '48 actividades con respuestas de 1 a 5'],
    ['2. Perfil', '6 puntajes RIASEC normalizados'],
    ['3. Modelo', 'Compara con 40 carreras del catálogo'],
    ['4. Resultado', 'Muestra 3 carreras para explorar'],
  ], 156, 386, [336, 788], 22);
  note(s, 'AMAI se conserva en los datos previos, pero no interviene en el modelo RIASEC.');
  s.speakerNotes.text = `Fuentes: ${report}; ${path.join(root, 'backend/README.md')}; ${path.join(root, 'frontend/README.md')}`;
}

// 5. Results
{
  const s = slide();
  title(s, 'Resultado de la prueba separada');
  table(s, [
    ['Medida', 'Resultado'],
    ['Casos para entrenar / probar', '32.330 / 8.083'],
    ['Carreras en el catálogo', '40'],
    ['Carrera declarada entre las 3 primeras', '47,1 %'],
    ['Carreras que aparecieron en el top 3', '38 de 40'],
  ], 156, 386, [790, 334], 21);
  note(s, 'La prueba mide coincidencia con la carrera declarada; no mide satisfacción futura.');
  s.speakerNotes.text = `Fuentes: ${report}; ${metrics}`;
}

// 6. Limits and next decision
{
  const s = slide();
  title(s, 'Límites antes de confiar en cada opción');
  text(s, '17 carreras no acertaron como primera opción en la prueba.', 86, 179, 1100, 64, 27);
  text(s, 'Solo 85 casos elegibles tienen MX como país de conexión.', 86, 286, 1100, 64, 27);
  text(s, 'Las cuatro etiquetas Hereford originales no equivalen al catálogo RIASEC.', 86, 393, 1100, 75, 27);
  text(s, 'Siguiente paso: revisar carreras débiles antes de usarlas como recomendaciones firmes.', 86, 545, 1080, 85, 22, true);
  s.speakerNotes.text = `Fuentes: ${report}; ${summary}; ${metrics}. País corresponde a ubicación de red, no nacionalidad confirmada.`;
}

await fs.mkdir(build, { recursive: true });
await fs.mkdir(path.dirname(output), { recursive: true });
for (let i = 0; i < ppt.slides.items.length; i++) {
  const blob = await ppt.export({ slide: ppt.slides.items[i], format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `slide-${i + 1}.png`), new Uint8Array(await blob.arrayBuffer()));
}

const candidate = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(ppt)).save(candidate);
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const result = await finalizePresentation({
  explicitTotalSlideCount: 6,
  workspaceDir: root,
  candidatePath: candidate,
  finalPath: output,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: [
    '--expected-slide-size-emu', '12192000,6858000',
    '--validate-heading-fit',
    '--require-native-table-slide', '2',
    '--require-native-table-slide', '3',
    '--require-native-table-slide', '4',
    '--require-native-table-slide', '5',
  ],
  requiredNativeTableOwnerSlides: [2, 3, 4, 5],
  requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: [font, 'Aptos'] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(build, 'validation-v2.json'),
});
console.log(JSON.stringify({ output, result }));
