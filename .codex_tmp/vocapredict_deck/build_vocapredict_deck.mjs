import fs from "node:fs/promises";
import path from "node:path";
import JSZip from "jszip";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/cisnerosbe/Documents/DOCCOM/Proyectos/vocapredict";
const TMP = path.join(ROOT, ".codex_tmp/vocapredict_deck");
const ASSETS = path.join(TMP, "assets");
const FINAL = path.join(ROOT, "VocaPredict_presentacion.pptx");

const W = 1280;
const H = 720;
const COLORS = {
  green: "#2C5234",
  gold: "#9C8412",
  cream: "#FBF8EF",
  creamDeep: "#F2EAD0",
  ink: "#1F261F",
  muted: "#697168",
  line: "#E2DED0",
  paleGreen: "#EEF6F0",
};

async function bytes(file) {
  return new Uint8Array(await fs.readFile(file));
}

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

function setNotes(slide, lines, sources = []) {
  slide.speakerNotes.textFrame.setText([
    ...lines,
    "",
    "[Sources]",
    ...sources,
  ]);
  slide.speakerNotes.setVisible(true);
}

function text(slide, name, content, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = content;
  shape.text.style = {
    fontSize: 24,
    color: COLORS.ink,
    ...style,
  };
  return shape;
}

function title(slide, content, top = 62, width = 720) {
  return text(slide, "title", content, { left: 76, top, width, height: 118 }, {
    fontSize: 44,
    bold: true,
    color: COLORS.ink,
  });
}

function kicker(slide, content, top = 42) {
  return text(slide, "kicker", content, { left: 78, top, width: 420, height: 30 }, {
    fontSize: 14,
    bold: true,
    color: COLORS.green,
  });
}

function body(slide, content, position, size = 22) {
  return text(slide, "body-copy", content, position, {
    fontSize: size,
    color: COLORS.muted,
  });
}

function rounded(slide, name, position, fill = "white", line = COLORS.line) {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: "rounded-2xl",
    shadow: "shadow-sm",
  });
}

async function image(slide, name, file, position, opts = {}) {
  return slide.images.add({
    blob: await bytes(file),
    contentType: "image/png",
    alt: opts.alt ?? name,
    fit: opts.fit ?? "contain",
    position,
    geometry: opts.geometry ?? "roundRect",
    borderRadius: opts.borderRadius ?? "rounded-2xl",
  });
}

function footer(slide, number) {
  text(slide, "footer", String(number).padStart(2, "0"), {
    left: 1164,
    top: 654,
    width: 40,
    height: 24,
  }, {
    fontSize: 14,
    bold: true,
    color: COLORS.line,
    alignment: "right",
  });
}

function addMiniStep(slide, index, label, x, y, active = false) {
  const fill = active ? COLORS.green : COLORS.paleGreen;
  const line = active ? COLORS.green : COLORS.line;
  rounded(slide, `step-${index}`, { left: x, top: y, width: 172, height: 72 }, fill, line);
  text(slide, `step-label-${index}`, label, { left: x + 18, top: y + 18, width: 136, height: 34 }, {
    fontSize: 18,
    bold: true,
    color: active ? "white" : COLORS.green,
    alignment: "center",
  });
}

function addArrow(slide, name, x1, y1, x2, y2) {
  slide.shapes.add({
    geometry: "line",
    name,
    position: { left: x1, top: y1, width: x2 - x1, height: y2 - y1 },
    line: { style: "solid", fill: COLORS.gold, width: 2, beginArrowType: "none", endArrowType: "triangle" },
  });
}

async function addFadeTransitions(pptxPath) {
  const zip = await JSZip.loadAsync(await fs.readFile(pptxPath));
  const slideFiles = Object.keys(zip.files)
    .filter((file) => /^ppt\/slides\/slide\d+\.xml$/.test(file))
    .sort((a, b) => Number(a.match(/slide(\d+)/)[1]) - Number(b.match(/slide(\d+)/)[1]));

  for (const file of slideFiles) {
    let xml = await zip.file(file).async("string");
    if (xml.includes("<p:transition")) continue;
    const transition = '<p:transition spd="med" advClick="1"><p:fade/></p:transition>';
    if (xml.includes("<p:clrMapOvr")) {
      xml = xml.replace(/(<p:clrMapOvr[\s\S]*?<\/p:clrMapOvr>|<p:clrMapOvr[^>]*\/>)/, `$1${transition}`);
    } else {
      xml = xml.replace("</p:cSld>", `</p:cSld>${transition}`);
    }
    zip.file(file, xml);
  }

  const next = await zip.generateAsync({ type: "nodebuffer" });
  await fs.writeFile(pptxPath, next);
}

async function main() {
  await fs.mkdir(path.join(TMP, "rendered"), { recursive: true });
  await fs.writeFile(path.join(TMP, "source-notes.txt"), [
    "VocaPredict presentation sources:",
    "- Local project README: backend/README.md",
    "- Local frontend source: frontend/src/pages, frontend/src/questions, frontend/src/amai.js",
    "- Screenshots captured locally from http://127.0.0.1:3000/",
    "- Backend local endpoint: http://127.0.0.1:8080/predict",
    "- AMAI NSE FAQ: https://www.amai.org/NSE/index.php?queVeo=preguntas",
    "- AMAI 2024 rule: https://www.amai.org/NSE/index.php?queVeo=NSE2024",
  ].join("\n"));

  const logo = path.join(ROOT, "frontend/public/assets/logo-home.png");
  const home = path.join(ASSETS, "home.png");
  const hereford = path.join(ASSETS, "question_hereford.png");
  const socio = path.join(ASSETS, "question_socio.png");
  const results = path.join(ASSETS, "results.png");
  const prediction = path.join(ASSETS, "prediction.png");

  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 1
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    await image(slide, "logo", logo, { left: 74, top: 68, width: 210, height: 122 }, { fit: "contain", geometry: "rect" });
    text(slide, "main-title", "VocaPredict", { left: 76, top: 224, width: 610, height: 88 }, {
      fontSize: 60,
      bold: true,
      color: COLORS.green,
    });
    body(slide, "Una herramienta que combina intereses vocacionales y contexto socioeconómico para apoyar una sugerencia de carrera.", {
      left: 80,
      top: 330,
      width: 540,
      height: 136,
    }, 27);
    await image(slide, "home-screenshot", home, { left: 706, top: 74, width: 488, height: 456 }, { fit: "contain" });
    rounded(slide, "closing-line", { left: 80, top: 560, width: 412, height: 54 }, COLORS.cream, COLORS.creamDeep);
    text(slide, "closing-line-text", "Presentación general del proyecto", { left: 108, top: 574, width: 356, height: 24 }, {
      fontSize: 20,
      bold: true,
      color: COLORS.ink,
    });
    footer(slide, 1);
    setNotes(slide, [
      "Abrir con la idea principal: VocaPredict no sustituye una orientación humana; organiza información relevante para iniciar una conversación mejor informada.",
      "La presentación evita detalles técnicos y muestra el recorrido visible para el usuario.",
    ], [
      "backend/README.md",
      "Captura de https://ionic-react-quiz-app.fly.dev/home",
    ]);
  }

  // 2
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "EL PROBLEMA");
    title(slide, "Elegir carrera suele mezclar gustos, contexto y dudas");
    await image(slide, "question-screenshot", hereford, { left: 676, top: 82, width: 504, height: 438 }, { fit: "contain" });
    body(slide, "VocaPredict convierte respuestas dispersas en una lectura ordenada: qué áreas interesan más, qué contexto acompaña al estudiante y qué carrera sugiere el modelo.", {
      left: 80,
      top: 232,
      width: 492,
      height: 154,
    }, 26);
    addMiniStep(slide, 1, "Intereses", 88, 468, true);
    addMiniStep(slide, 2, "Contexto", 292, 468);
    addMiniStep(slide, 3, "Sugerencia", 496, 468);
    addArrow(slide, "arrow-1", 260, 504, 292, 504);
    addArrow(slide, "arrow-2", 464, 504, 496, 504);
    footer(slide, 2);
    setNotes(slide, [
      "Explicar que el valor está en reunir tres piezas en una experiencia sencilla: preferencias, datos socioeconómicos y una sugerencia final.",
      "Evitar venderlo como decisión automática; presentarlo como apoyo para orientación.",
    ], [
      "frontend/src/pages/Home.jsx",
      "frontend/src/questions/index.js",
      "Captura de https://ionic-react-quiz-app.fly.dev/questions",
    ]);
  }

  // 3
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "RECORRIDO");
    title(slide, "El usuario avanza por un flujo guiado y sin cambios bruscos", 62, 820);
    await image(slide, "home", home, { left: 74, top: 210, width: 336, height: 250 }, { fit: "cover" });
    await image(slide, "question", hereford, { left: 472, top: 210, width: 336, height: 250 }, { fit: "cover" });
    await image(slide, "result", prediction, { left: 870, top: 210, width: 336, height: 250 }, { fit: "cover" });
    addArrow(slide, "flow-arrow-1", 420, 334, 462, 334);
    addArrow(slide, "flow-arrow-2", 818, 334, 860, 334);
    text(slide, "caption-1", "Inicio claro", { left: 88, top: 482, width: 300, height: 34 }, { fontSize: 22, bold: true, color: COLORS.green, alignment: "center" });
    text(slide, "caption-2", "Preguntas paso a paso", { left: 488, top: 482, width: 300, height: 34 }, { fontSize: 22, bold: true, color: COLORS.green, alignment: "center" });
    text(slide, "caption-3", "Resultado entendible", { left: 884, top: 482, width: 300, height: 34 }, { fontSize: 22, bold: true, color: COLORS.green, alignment: "center" });
    body(slide, "La pantalla muestra el avance, evita saturar y puede retomar el cuestionario si queda a medias.", {
      left: 220,
      top: 568,
      width: 840,
      height: 52,
    }, 24);
    footer(slide, 3);
    setNotes(slide, [
      "Resaltar que la experiencia está pensada para reducir fricción: una pregunta por vez, progreso visible y resultado final concentrado.",
      "Sugerencia de animación: mostrar las tres capturas una por una con aparición suave.",
    ], [
      "frontend/src/pages/Home.jsx",
      "frontend/src/pages/Questions.jsx",
      "frontend/src/pages/Prediction.jsx",
      "Capturas locales de http://127.0.0.1:3000/",
    ]);
  }

  // 4
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "CUESTIONARIOS");
    title(slide, "Intereses primero; contexto después", 62, 820);
    await image(slide, "hereford-screen", hereford, { left: 74, top: 184, width: 520, height: 340 }, { fit: "contain" });
    await image(slide, "socio-screen", socio, { left: 686, top: 184, width: 520, height: 340 }, { fit: "contain" });
    text(slide, "left-label", "Inventario de intereses", { left: 144, top: 560, width: 380, height: 34 }, { fontSize: 24, bold: true, color: COLORS.green, alignment: "center" });
    text(slide, "right-label", "Estudio socioeconómico", { left: 756, top: 560, width: 380, height: 34 }, { fontSize: 24, bold: true, color: COLORS.green, alignment: "center" });
    body(slide, "La primera parte mide afinidad por actividades. La segunda parte ayuda a contextualizar la recomendación.", {
      left: 232,
      top: 620,
      width: 816,
      height: 42,
    }, 22);
    footer(slide, 4);
    setNotes(slide, [
      "Explicar que Hereford pregunta por actividades concretas, no por carreras directamente.",
      "El estudio socioeconómico no reemplaza la orientación; agrega contexto para enriquecer la sugerencia.",
    ], [
      "frontend/src/questions/index.js",
      "frontend/src/pages/Questions.jsx",
      "Capturas de https://ionic-react-quiz-app.fly.dev/questions",
    ]);
  }

  // 5
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "CONTEXTO AMAI");
    title(slide, "AMAI es una regla mexicana para clasificar hogares", 62, 850);

    rounded(slide, "origin-panel", { left: 76, top: 214, width: 408, height: 292 }, COLORS.cream, COLORS.creamDeep);
    text(slide, "amai-word", "AMAI", { left: 120, top: 260, width: 320, height: 76 }, {
      fontSize: 58,
      bold: true,
      color: COLORS.green,
      alignment: "center",
    });
    body(slide, "Asociación Mexicana de Agencias de Inteligencia de Mercado y Opinión", {
      left: 122,
      top: 350,
      width: 316,
      height: 78,
    }, 24);
    text(slide, "origin-note", "No nace como metodología gubernamental; se apoya en datos oficiales para sus estimaciones.", {
      left: 110,
      top: 448,
      width: 340,
      height: 46,
    }, {
      fontSize: 17,
      color: COLORS.muted,
      alignment: "center",
    });

    const facts = [
      ["Origen", "La desarrolla y actualiza el Comité de Niveles Socioeconómicos de AMAI."],
      ["Base oficial", "Usa información de la ENIGH, levantada por INEGI, para estimar proporciones."],
      ["Uso", "Ayuda a comparar hogares con una regla común en investigación, academia e instituciones públicas."],
    ];
    facts.forEach(([label, desc], i) => {
      const y = 194 + i * 116;
      slide.shapes.add({
        geometry: "ellipse",
        name: `fact-dot-${i}`,
        position: { left: 570, top: y + 14, width: 48, height: 48 },
        fill: i === 1 ? COLORS.gold : COLORS.green,
        line: { style: "solid", fill: i === 1 ? COLORS.gold : COLORS.green, width: 1 },
      });
      text(slide, `fact-number-${i}`, String(i + 1), { left: 570, top: y + 27, width: 48, height: 22 }, {
        fontSize: 20,
        bold: true,
        color: "white",
        alignment: "center",
      });
      text(slide, `fact-title-${i}`, label, { left: 642, top: y, width: 424, height: 34 }, {
        fontSize: 25,
        bold: true,
        color: COLORS.green,
      });
      body(slide, desc, { left: 642, top: y + 38, width: 500, height: 58 }, 20);
    });

    rounded(slide, "vocapredict-use", { left: 174, top: 572, width: 932, height: 56 }, COLORS.paleGreen, COLORS.line);
    text(slide, "vocapredict-use-text", "En VocaPredict, AMAI permite resumir el contexto del hogar en un valor comparable para el modelo.", {
      left: 214,
      top: 589,
      width: 852,
      height: 24,
    }, {
      fontSize: 20,
      bold: true,
      color: COLORS.green,
      alignment: "center",
    });
    footer(slide, 5);
    setNotes(slide, [
      "Aclaración importante: AMAI no debe presentarse como una metodología creada por el gobierno de México.",
      "La regla la desarrolla AMAI; su conexión con fuentes oficiales viene del uso de la ENIGH de INEGI para estimaciones y revisión metodológica.",
      "Este contexto ayuda a explicar por qué VocaPredict pregunta por vivienda, escolaridad, autos, internet y personas que trabajan.",
    ], [
      "AMAI Preguntas frecuentes NSE: https://www.amai.org/NSE/index.php?queVeo=preguntas",
      "AMAI Estimaciones NSE 2022 y Regla AMAI 2024: https://www.amai.org/NSE/index.php?queVeo=NSE2024",
    ]);
  }

  // 6
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "AMAI");
    title(slide, "AMAI resume el contexto del hogar en un indicador simple", 62, 790);
    rounded(slide, "amai-panel", { left: 72, top: 204, width: 470, height: 330 }, COLORS.cream, COLORS.creamDeep);
    text(slide, "amai-big", "0 → 1", { left: 124, top: 256, width: 360, height: 86 }, {
      fontSize: 58,
      bold: true,
      color: COLORS.green,
      alignment: "center",
    });
    body(slide, "Cerca de 0 indica condiciones más limitadas. Cerca de 1 indica condiciones más favorables.", {
      left: 122,
      top: 358,
      width: 370,
      height: 82,
    }, 25);
    const levels = ["E", "D", "D+", "C-", "C", "C+", "A/B"];
    levels.forEach((level, i) => {
      const x = 634 + i * 70;
      slide.shapes.add({
        geometry: "ellipse",
        name: `level-${level}`,
        position: { left: x, top: 285, width: 52, height: 52 },
        fill: i >= 4 ? COLORS.green : COLORS.paleGreen,
        line: { style: "solid", fill: i >= 4 ? COLORS.green : COLORS.line, width: 1 },
      });
      text(slide, `level-label-${level}`, level, { left: x - 6, top: 300, width: 64, height: 22 }, {
        fontSize: level === "A/B" ? 17 : 19,
        bold: true,
        color: i >= 4 ? "white" : COLORS.green,
        alignment: "center",
      });
    });
    body(slide, "El sistema calcula puntos con respuestas del hogar y después asigna una letra: E, D, C, C+, A/B.", {
      left: 626,
      top: 386,
      width: 516,
      height: 80,
    }, 25);
    footer(slide, 6);
    setNotes(slide, [
      "AMAI se puede explicar como una forma estandarizada de resumir condiciones del hogar en una sola lectura.",
      "La normalización 0 a 1 sirve para que el modelo pueda usar el dato junto con los intereses sin mezclar escalas incompatibles.",
    ], [
      "frontend/src/amai.js",
      "backend/docs/reporte_aplicacion_amai.md",
      "AMAI Preguntas frecuentes NSE: https://www.amai.org/NSE/index.php?queVeo=preguntas",
    ]);
  }

  // 7
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "MODELO");
    title(slide, "La predicción usa diez señales, no una sola respuesta", 62, 820);
    const startX = 84;
    const startY = 214;
    const labels = ["Cálculo", "Físico", "Biológico", "Mecánico", "Social", "Literario", "Persuasivo", "Artístico", "Musical", "AMAI"];
    labels.forEach((label, i) => {
      const x = startX + (i % 5) * 218;
      const y = startY + Math.floor(i / 5) * 128;
      rounded(slide, `signal-${i}`, { left: x, top: y, width: 176, height: 78 }, i === 9 ? COLORS.cream : COLORS.paleGreen, i === 9 ? COLORS.gold : COLORS.line);
      text(slide, `signal-text-${i}`, label, { left: x + 12, top: y + 25, width: 152, height: 26 }, {
        fontSize: 21,
        bold: true,
        color: i === 9 ? COLORS.gold : COLORS.green,
        alignment: "center",
      });
    });
    body(slide, "Las nueve primeras señales vienen del inventario vocacional. La décima es el valor AMAI normalizado.", {
      left: 170,
      top: 506,
      width: 940,
      height: 58,
    }, 26);
    footer(slide, 7);
    setNotes(slide, [
      "Evitar tecnicismos: decir que el modelo busca patrones entre perfiles anteriores y las respuestas actuales.",
      "Si alguien pregunta por 'modelo', explicar que es una fórmula entrenada con ejemplos para sugerir la clase más parecida.",
    ], [
      "backend/README.md",
      "frontend/src/pages/Results.jsx",
    ]);
  }

  // 8
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "MÓDULOS");
    title(slide, "Cada módulo cumple una función clara dentro del sistema", 62, 820);
    const modules = [
      ["Frontend", "Lo que ve y responde el usuario"],
      ["Cuestionarios", "Preguntas Hereford y socioeconómicas"],
      ["AMAI", "Convierte contexto en un valor comparable"],
      ["Modelo", "Genera la sugerencia vocacional"],
      ["API", "Conecta la app con la predicción"],
      ["Progreso local", "Permite retomar si se interrumpe"],
    ];
    modules.forEach(([name, desc], i) => {
      const x = 82 + (i % 3) * 384;
      const y = 202 + Math.floor(i / 3) * 174;
      rounded(slide, `module-${i}`, { left: x, top: y, width: 314, height: 112 }, "white", COLORS.line);
      text(slide, `module-name-${i}`, name, { left: x + 24, top: y + 22, width: 260, height: 30 }, {
        fontSize: 26,
        bold: true,
        color: COLORS.green,
      });
      body(slide, desc, { left: x + 24, top: y + 62, width: 260, height: 38 }, 18);
    });
    footer(slide, 8);
    setNotes(slide, [
      "Presentar los módulos como una cadena de responsabilidades, no como una lista técnica.",
      "La idea clave: la app pregunta, ordena, calcula y consulta el modelo; el backend responde con la sugerencia.",
    ], [
      "backend/README.md",
      "frontend/src/App.jsx",
      "frontend/src/pages/Results.jsx",
      "backend/serve.py",
    ]);
  }

  // 9
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    kicker(slide, "RESULTADO");
    title(slide, "La salida muestra perfil, AMAI y sugerencia del modelo", 62, 820);
    await image(slide, "results-screen", results, { left: 72, top: 200, width: 520, height: 350 }, { fit: "contain" });
    await image(slide, "prediction-screen", prediction, { left: 688, top: 200, width: 520, height: 350 }, { fit: "contain" });
    body(slide, "Primero se revisa el perfil de intereses. Después se envían los datos y aparece una carrera sugerida.", {
      left: 190,
      top: 584,
      width: 900,
      height: 54,
    }, 24);
    footer(slide, 9);
    setNotes(slide, [
      "Mostrar que el resultado no solo da una etiqueta: también permite revisar el perfil por áreas y el indicador AMAI.",
      "Sugerencia de animación: resultados primero, predicción después, con aparición discreta.",
    ], [
      "frontend/src/pages/Results.jsx",
      "frontend/src/pages/Prediction.jsx",
      "Capturas de https://ionic-react-quiz-app.fly.dev/results y /prediction",
    ]);
  }

  // 10
  {
    const slide = deck.slides.add();
    slide.background.fill = "white";
    await image(slide, "logo", logo, { left: 76, top: 70, width: 174, height: 106 }, { fit: "contain", geometry: "rect" });
    title(slide, "VocaPredict ayuda a conversar mejor sobre el futuro", 214, 850);
    body(slide, "No decide por la persona. Ordena información, muestra patrones y ofrece una sugerencia inicial para orientar la siguiente conversación.", {
      left: 80,
      top: 360,
      width: 650,
      height: 104,
    }, 27);
    rounded(slide, "next", { left: 820, top: 268, width: 310, height: 168 }, COLORS.cream, COLORS.creamDeep);
    text(slide, "next-title", "Mensaje final", { left: 858, top: 306, width: 234, height: 32 }, {
      fontSize: 26,
      bold: true,
      color: COLORS.green,
      alignment: "center",
    });
    body(slide, "Tecnología como apoyo, no como sustituto de la orientación.", {
      left: 858,
      top: 356,
      width: 234,
      height: 50,
    }, 20);
    footer(slide, 10);
    setNotes(slide, [
      "Cerrar reforzando el valor humano: VocaPredict abre una conversación más informada, no dicta una decisión.",
      "Invitar a preguntas sobre el flujo, datos o próximos ajustes visuales.",
    ], [
      "backend/README.md",
      "frontend/src/pages/Home.jsx",
    ]);
  }

  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL);
  await addFadeTransitions(FINAL);

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(TMP, "rendered", `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(path.join(TMP, "rendered", `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }
  await writeBlob(path.join(TMP, "rendered", "montage.webp"), await deck.export({ format: "webp", montage: true, scale: 1 }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
