import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputXlsx =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/conjunto_de_datos_reetiquetados.xlsx";
const augmentedCsv =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/data/conjunto_de_datos_aumentado_75_sintetico.csv";
const outputXlsx =
  "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict/conjunto_de_datos_aumentado_75_sintetico.xlsx";
const previewPng =
  "/private/tmp/vocapredict-conjunto-aumentado-75-sintetico-preview.png";

const lines = (await fs.readFile(augmentedCsv, "utf8")).trim().split("\n");
const values = lines.slice(1).map((line) => {
  const cells = line.split(",");
  return [...cells.slice(0, 9).map(Number), cells[9]];
});
const input = await FileBlob.load(inputXlsx);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Hoja1");

sheet.getRange(`A2:J${values.length + 1}`).values = values;

const preview = await workbook.inspect({
  kind: "table",
  range: "Hoja1!A1:J12",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 10,
});
const rendered = await workbook.render({
  sheetName: "Hoja1",
  range: "A1:J24",
  scale: 1.4,
});
const exported = await SpreadsheetFile.exportXlsx(workbook);

await exported.save(outputXlsx);
await fs.writeFile(previewPng, Buffer.from(await rendered.arrayBuffer()));
console.log(
  JSON.stringify({ outputXlsx, previewPng, preview: preview.ndjson }, null, 2),
);
