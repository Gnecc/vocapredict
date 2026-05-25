import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputXlsx =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/conjunto_de_datos_normalizados.xlsx";
const auditCsv =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/data/auditoria_reetiquetado.csv";
const outputXlsx =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/conjunto_de_datos_reetiquetados.xlsx";
const previewPng =
  "/private/tmp/vocapredict-conjunto-de-datos-reetiquetados-preview.png";

const auditLines = (await fs.readFile(auditCsv, "utf8")).trim().split("\n");
const newLabels = auditLines.slice(1).map((line) => line.split(",")[2]);
const input = await FileBlob.load(inputXlsx);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Hoja1");

sheet.getRange(`J2:J${newLabels.length + 1}`).values = newLabels.map((label) => [
  label,
]);

const preview = await workbook.inspect({
  kind: "table",
  range: "Hoja1!A1:J8",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 10,
});
const exported = await SpreadsheetFile.exportXlsx(workbook);
const rendered = await workbook.render({
  sheetName: "Hoja1",
  range: "A1:J24",
  scale: 1.4,
});

await exported.save(outputXlsx);
await fs.writeFile(previewPng, Buffer.from(await rendered.arrayBuffer()));
console.log(
  JSON.stringify({ outputXlsx, previewPng, preview: preview.ndjson }, null, 2),
);
