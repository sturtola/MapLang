const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" x 7.5"
pres.author = "Riveros, Riveros, Scetti, Turtola";
pres.title = "MapLang — Trabajo Integrador TC2026";

// ---------------------------------------------------------------
// Paleta dark / gold (consistente con la identidad del proyecto)
// ---------------------------------------------------------------
const BG_DARK = "1B1B1F";
const BG_DARK2 = "232328";
const GOLD = "D4AF37";
const GOLD_SOFT = "E8C766";
const WHITE = "F5F5F5";
const GRAY = "9A9AA2";
const GREEN = "3DDC97";
const RED = "E74C3C";
const YELLOW = "F1C40F";
const PURPLE = "8E44AD";
const BLUE = "3498DB";

const FONT_HEAD = "Bookman Old Style";
const FONT_BODY = "Calibri";

function bgSlide(slide, color = BG_DARK) {
  slide.background = { color };
}

function pageNum(slide, n) {
  slide.addText(`${n}`, {
    x: 12.55, y: 7.05, w: 0.6, h: 0.3,
    fontFace: FONT_BODY, fontSize: 11, color: GRAY, align: "right",
  });
}

function kicker(slide, text) {
  slide.addText(text.toUpperCase(), {
    x: 0.6, y: 0.45, w: 8, h: 0.4,
    fontFace: FONT_BODY, fontSize: 13, color: GOLD, bold: true, charSpacing: 2,
  });
}

function title(slide, text, opts = {}) {
  slide.addText(text, {
    x: 0.6, y: opts.y || 0.82, w: opts.w || 11.5, h: opts.h || 0.9,
    fontFace: FONT_HEAD, fontSize: opts.size || 32, color: WHITE, bold: true,
  });
}

// =================================================================
// SLIDE 1 — Portada
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);

  s.addShape(pres.shapes.OVAL, {
    x: 9.7, y: -2.3, w: 6, h: 6, fill: { color: GOLD, transparency: 92 }, line: { type: "none" },
  });
  s.addShape(pres.shapes.OVAL, {
    x: -2.5, y: 4.5, w: 5, h: 5, fill: { color: GOLD, transparency: 94 }, line: { type: "none" },
  });

  s.addText("TEORÍA DE LA COMPUTACIÓN — TRABAJO INTEGRADOR 2026", {
    x: 0.9, y: 1.7, w: 10, h: 0.4, fontFace: FONT_BODY, fontSize: 14,
    color: GOLD, bold: true, charSpacing: 2,
  });
  s.addText("MapLang", {
    x: 0.85, y: 2.15, w: 10, h: 1.4, fontFace: FONT_HEAD, fontSize: 64,
    color: WHITE, bold: true,
  });
  s.addText("Un Lenguaje de Dominio Específico para Describir\nMapas de Videojuegos Dungeon-Crawler", {
    x: 0.9, y: 3.55, w: 9.5, h: 1.0, fontFace: FONT_BODY, fontSize: 20,
    color: GRAY, italic: true,
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.9, y: 4.75, w: 1.3, h: 0.04, fill: { color: GOLD }, line: { type: "none" },
  });

  s.addText([
    { text: "Riveros, Lautaro   ·   Riveros, Maximo   ·   Scetti, Santiago   ·   Turtola, Sabrina", options: { breakLine: true } },
    { text: "Grupo 50 — Proyecto SIC-UNNE   |   FaCENA, UNNE", options: {} },
  ], {
    x: 0.9, y: 6.55, w: 10.5, h: 0.7, fontFace: FONT_BODY, fontSize: 13, color: GRAY,
  });
}

// =================================================================
// SLIDE 2 — Motivación y escenario (≈2 min)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "01 · Motivación y escenario");
  title(s, "¿Por qué un DSL para mapas de videojuegos?");

  const cards = [
    { t: "El problema", d: "Los editores de mapas comerciales son herramientas gráficas propietarias: no se pueden versionar como texto, ni generar proceduralmente.", color: RED },
    { t: "La propuesta", d: "MapLang: un lenguaje textual para describir habitaciones, atributos y conexiones de un dungeon-crawler, sin ambigüedades.", color: GREEN },
    { t: "El estándar real", d: "Tiled Map Editor y el sistema de tilemaps de Godot resuelven problemas análogos en la industria.", color: BLUE },
  ];

  let cardW = 3.55, gap = 0.35, startX = 0.6, y = 2.1, h = 3.55;
  cards.forEach((c, i) => {
    let x = startX + i * (cardW + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: cardW, h, rectRadius: 0.08,
      fill: { color: BG_DARK2 }, line: { color: c.color, width: 1.2 },
      shadow: { type: "outer", color: "000000", blur: 8, offset: 3, angle: 90, opacity: 0.35 },
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.3, y: y + 0.3, w: 0.55, h: 0.55, fill: { color: c.color }, line: { type: "none" },
    });
    s.addText(`${i + 1}`, {
      x: x + 0.3, y: y + 0.3, w: 0.55, h: 0.55, align: "center", valign: "middle",
      fontFace: FONT_HEAD, fontSize: 20, bold: true, color: BG_DARK,
    });
    s.addText(c.t, {
      x: x + 0.3, y: y + 1.0, w: cardW - 0.6, h: 0.5,
      fontFace: FONT_HEAD, fontSize: 18, bold: true, color: WHITE,
    });
    s.addText(c.d, {
      x: x + 0.3, y: y + 1.55, w: cardW - 0.6, h: h - 1.85,
      fontFace: FONT_BODY, fontSize: 13.5, color: GRAY, valign: "top",
    });
  });

  s.addText("Originalidad  ·  Riqueza gramatical  ·  Potencial visual  ·  Aplicabilidad real", {
    x: 0.6, y: 6.15, w: 11.5, h: 0.5, fontFace: FONT_BODY, fontSize: 14,
    italic: true, color: GOLD_SOFT, align: "center",
  });
  pageNum(s, 2);
}

// =================================================================
// SLIDE 3 — Alcance del lenguaje
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "01 · Motivación y escenario");
  title(s, "Alcance de MapLang");

  s.addText("Incluido en esta versión", {
    x: 0.6, y: 2.0, w: 5.6, h: 0.45, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: GREEN,
  });
  const incl = [
    "Mapas con nombre y dimensión N×M",
    "Habitaciones con coordenadas (x,y)",
    "6 atributos: TYPE, EXITS, ENEMY, LEVEL, ITEM, NPC",
    "Conexiones entre habitaciones, con etiqueta opcional",
    "Comentarios de línea y espacios en blanco ignorados",
  ];
  s.addText(incl.map(t => ({ text: t, options: { bullet: { code: "2713" }, breakLine: true, color: WHITE } })), {
    x: 0.6, y: 2.55, w: 5.6, h: 3.6, fontFace: FONT_BODY, fontSize: 15, valign: "top", lineSpacing: 28,
  });

  s.addText("Excluido (versión actual)", {
    x: 6.85, y: 2.0, w: 5.6, h: 0.45, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: RED,
  });
  const excl = [
    "Lógica de eventos / triggers dentro de salas",
    "Herencia entre tipos de habitación",
    "Mapas multi-piso (se tratan como mapas independientes)",
  ];
  s.addText(excl.map(t => ({ text: t, options: { bullet: { code: "2717" }, breakLine: true, color: WHITE } })), {
    x: 6.85, y: 2.55, w: 5.6, h: 3.6, fontFace: FONT_BODY, fontSize: 15, valign: "top", lineSpacing: 28,
  });

  s.addShape(pres.shapes.LINE, {
    x: 6.45, y: 2.05, w: 0, h: 3.6, line: { color: BG_DARK2, width: 2 },
  });
  pageNum(s, 3);
}

// =================================================================
// SLIDE 4 — Gramática formal: clase y producciones (≈4 min)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "02 · Gramática formal");
  title(s, "Una GLC de 20 producciones");

  s.addText([
    { text: "Gramática Libre de Contexto (GLC, Tipo 2)", options: { bold: true, color: GOLD_SOFT, breakLine: true } },
    { text: "Cada producción: A → ω,  con A ∈ N  y  ω ∈ (N ∪ T)*", options: { color: WHITE, breakLine: true } },
  ], { x: 0.6, y: 2.0, w: 11.5, h: 0.9, fontFace: FONT_BODY, fontSize: 16, valign: "top" });

  const rows = [
    ["P1", "<programa>", '<mapa>+'],
    ["P2", "<mapa>", '"MAP" <cadena> "SIZE" <dimension> "{" <cuerpo> "}"'],
    ["P5", "<sala>", '"ROOM" "(" <ent>"," <ent> ")" <atributo>+'],
    ["P6", "<atributo>", "<tipo_sala> | <salidas> | <enemigo> | <nivel> | <item> | <npc>"],
    ["P16", "<conexion>", '"CONNECT" "("<ent>","<ent>")" "->" "("<ent>","<ent>")" ["via" <cadena>]'],
  ];

  let tableRows = [
    [
      { text: "#", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
      { text: "No terminal", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
      { text: "Producción (extracto)", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
    ],
  ];
  rows.forEach(r => {
    tableRows.push([
      { text: r[0], options: { color: WHITE, fontFace: "Consolas" } },
      { text: r[1], options: { color: GREEN, fontFace: "Consolas" } },
      { text: r[2], options: { color: GRAY, fontFace: "Consolas", fontSize: 12 } },
    ]);
  });

  s.addTable(tableRows, {
    x: 0.6, y: 3.0, w: 11.5, h: 3.4,
    colW: [0.7, 2.3, 8.5],
    fontSize: 13, fontFace: FONT_BODY,
    border: { type: "solid", color: BG_DARK2, pt: 1 },
    fill: { color: BG_DARK },
    autoPage: false,
    valign: "middle",
    rowH: 0.62,
  });

  s.addText("20 producciones completas en GRAMMAR.md y en el informe técnico (Tabla 1)", {
    x: 0.6, y: 6.65, w: 11.5, h: 0.4, fontFace: FONT_BODY, fontSize: 12, italic: true, color: GRAY,
  });
  pageNum(s, 4);
}

// =================================================================
// SLIDE 5 — Decisiones de diseño y no ambigüedad
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "02 · Gramática formal");
  title(s, "Decisiones de diseño clave");

  const items = [
    { t: "Palabras clave distintivas", d: "Cada atributo (TYPE, EXITS, ENEMY...) arranca con una keyword única → FIRST() disjuntos, cero conflictos de predicción." },
    { t: "Orden libre de atributos", d: "<atributo>+ admite cualquier orden dentro de ROOM, sin ambigüedad: cada alternativa sigue siendo reconocible por su keyword." },
    { t: "Conexión con etiqueta opcional", d: '[ "via" <cadena> ] se resuelve con 1 token de lookahead: "via" no pertenece a FOLLOW(<conexion>).' },
  ];

  let y = 2.05;
  items.forEach((it, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.6, y, w: 11.5, h: 1.35, rectRadius: 0.06,
      fill: { color: BG_DARK2 }, line: { color: GOLD, width: 0.75 },
    });
    s.addText(it.t, {
      x: 0.95, y: y + 0.12, w: 10.8, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: GOLD_SOFT,
    });
    s.addText(it.d, {
      x: 0.95, y: y + 0.58, w: 10.8, h: 0.65, fontFace: FONT_BODY, fontSize: 13.5, color: WHITE,
    });
    y += 1.55;
  });

  pageNum(s, 5);
}

// =================================================================
// SLIDE 6 — No ambigüedad + LL(1)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "02 · Gramática formal");
  title(s, "No ambigüedad y condición LL(1)");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 2.0, w: 5.6, h: 4.3, rectRadius: 0.08,
    fill: { color: BG_DARK2 }, line: { color: GREEN, width: 1 },
  });
  s.addText("Sin ambigüedad", { x: 0.9, y: 2.2, w: 5, h: 0.4, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: GREEN });
  s.addText([
    { text: "Una GLC es ambigua  ⟺  alguna sentencia admite", options: { breakLine: true } },
    { text: "dos derivaciones por izquierda distintas.", options: { breakLine: true, color: GOLD_SOFT, italic: true } },
    { text: "  ", options: { breakLine: true } },
    { text: "• <sala> | <conexion>  →  ROOM vs CONNECT", options: { breakLine: true } },
    { text: "• <atributo> (6 var.)  →  6 keywords distintas", options: { breakLine: true } },
    { text: "• <tipo_valor> y <direccion>  →  literales únicos", options: { breakLine: true } },
    { text: "  ", options: { breakLine: true } },
    { text: "⇒ toda sentencia tiene un único árbol de derivación.", options: { bold: true } },
  ], { x: 0.9, y: 2.75, w: 5.0, h: 3.4, fontFace: FONT_BODY, fontSize: 13.5, color: WHITE, valign: "top" });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.55, y: 2.0, w: 5.6, h: 4.3, rectRadius: 0.08,
    fill: { color: BG_DARK2 }, line: { color: BLUE, width: 1 },
  });
  s.addText("Condición LL(1)", { x: 6.85, y: 2.2, w: 5, h: 0.4, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: BLUE });
  s.addText([
    { text: "FIRST(<sala>) = {ROOM}", options: { breakLine: true, fontFace: "Consolas" } },
    { text: "FIRST(<conexion>) = {CONNECT}", options: { breakLine: true, fontFace: "Consolas" } },
    { text: "→ disjuntos", options: { breakLine: true, color: GOLD_SOFT, italic: true } },
    { text: "  ", options: { breakLine: true } },
    { text: "FOLLOW(<conexion>) =", options: { breakLine: true, fontFace: "Consolas" } },
    { text: '{ROOM, CONNECT, "}"}', options: { breakLine: true, fontFace: "Consolas" } },
    { text: '"via" ∉ FOLLOW(<conexion>)', options: { breakLine: true, color: GOLD_SOFT, italic: true } },
    { text: "  ", options: { breakLine: true } },
    { text: "⇒ parser descendente recursivo sin backtracking.", options: { bold: true } },
  ], { x: 6.85, y: 2.75, w: 5.0, h: 3.4, fontFace: FONT_BODY, fontSize: 13, color: WHITE, valign: "top" });

  pageNum(s, 6);
}

// =================================================================
// SLIDE 7 — Implementación: arquitectura (≈6 min)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "03 · Implementación");
  title(s, "Arquitectura del sistema");

  s.addImage({ path: "figs/fig_arquitectura.png", x: 0.6, y: 2.3, w: 11.5, h: 2.6 });

  s.addText([
    { text: "Python 3.12", options: { bold: true, color: GOLD_SOFT } },
    { text: "  ·  Implementación manual del lexer y el parser (sin Flex/PLY/ANTLR)  ·  Tests con unittest  ·  Render con matplotlib", options: { color: WHITE } },
  ], { x: 0.6, y: 5.2, w: 11.5, h: 0.6, fontFace: FONT_BODY, fontSize: 15, align: "center" });

  s.addText("src/lexer.py · parser.py · ast_nodes.py · semantic.py · renderer.py · main.py", {
    x: 0.6, y: 6.0, w: 11.5, h: 0.5, fontFace: "Consolas", fontSize: 13, color: GRAY, align: "center",
  });
  pageNum(s, 7);
}

// =================================================================
// SLIDE 8 — Parser descendente recursivo + manejo de errores
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "03 · Implementación");
  title(s, "Parser descendente recursivo");

  s.addText("Cada no-terminal → una función Python", {
    x: 0.6, y: 2.0, w: 5.6, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: GOLD_SOFT,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 2.5, w: 5.6, h: 3.7, rectRadius: 0.06, fill: { color: "F5F5F0" }, line: { color: GOLD, width: 1 },
  });
  s.addText([
    { text: "if self.check_keyword(\"via\"):", options: { breakLine: true, color: "AA00AA" } },
    { text: "    self.advance()", options: { breakLine: true, color: "000000" } },
    { text: "    etiqueta_tok = self.expect_type(", options: { breakLine: true, color: "000000" } },
    { text: "        \"STRING\", \"una cadena\")", options: { breakLine: true, color: "008000" } },
    { text: "    etiqueta = etiqueta_tok.value", options: { color: "000000" } },
  ], { x: 0.85, y: 2.7, w: 5.1, h: 3.3, fontFace: "Consolas", fontSize: 14, valign: "top" });

  s.addText("Manejo y recuperación de errores", {
    x: 6.85, y: 2.0, w: 5.6, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: GOLD_SOFT,
  });
  const errFeatures = [
    "ParseError con línea, columna y mensaje claro",
    '"se esperaba \')\' pero se encontró \'TYPE\'"',
    "Modo pánico: sincroniza hasta ROOM/CONNECT/'}'",
    "Permite reportar varios errores en una sola pasada",
  ];
  s.addText(errFeatures.map(t => ({ text: t, options: { bullet: true, breakLine: true, color: WHITE } })), {
    x: 6.85, y: 2.5, w: 5.6, h: 3.5, fontFace: FONT_BODY, fontSize: 14.5, valign: "top", lineSpacing: 26,
  });
  pageNum(s, 8);
}

// =================================================================
// SLIDE 9 — AST y validación semántica
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "03 · Implementación");
  title(s, "Del AST a las reglas semánticas");

  s.addImage({ path: "figs/fig_ast_slide.png", x: 0.6, y: 2.05, w: 7.0, h: 2.0 });
  s.addText("AST de la Mazmorra del Dragón (Graphviz)", {
    x: 0.6, y: 4.1, w: 7.0, h: 0.35, fontFace: FONT_BODY, fontSize: 11.5, italic: true, color: GRAY, align: "center",
  });

  s.addText("Validaciones semánticas (semantic.py)", {
    x: 7.95, y: 2.05, w: 4.8, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: GOLD_SOFT,
  });
  const sem = [
    "S1 — Coordenadas dentro de SIZE N×M",
    "S2 — Sin coordenadas de sala duplicadas",
    "S3 — CONNECT referencia salas existentes",
    "S4 — Atributos no se repiten en una sala",
  ];
  s.addText(sem.map(t => ({ text: t, options: { bullet: true, breakLine: true, color: WHITE } })), {
    x: 7.95, y: 2.55, w: 4.8, h: 2.2, fontFace: FONT_BODY, fontSize: 13.5, valign: "top", lineSpacing: 24,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 4.65, w: 11.5, h: 1.75, rectRadius: 0.06, fill: { color: BG_DARK2 }, line: { color: RED, width: 1 },
  });
  s.addText("Ejemplo real de salida ante errores semánticos múltiples:", {
    x: 0.9, y: 4.8, w: 11, h: 0.35, fontFace: FONT_BODY, fontSize: 12.5, color: GOLD_SOFT, italic: true,
  });
  s.addText([
    { text: "Error semántico (línea 6): ya existe una sala declarada en (0,0)...", options: { breakLine: true } },
    { text: "Error semántico (línea 7): la sala (5,5) está fuera de los límites...", options: { breakLine: true } },
    { text: "Error semántico (línea 8): CONNECT referencia la sala (9,9) inexistente...", options: {} },
  ], { x: 0.9, y: 5.15, w: 11, h: 1.2, fontFace: "Consolas", fontSize: 11.5, color: "FF8A80", valign: "top" });

  pageNum(s, 9);
}

// =================================================================
// SLIDE 10 — Demostración en vivo (≈5 min)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "04 · Demostración en vivo");
  title(s, "De texto a mapa renderizado");

  s.addImage({ path: "figs/fig_mapa_dragon.png", x: 0.6, y: 2.0, w: 11.5, h: 2.45 });

  s.addText([
    { text: "$ python3 main.py mazmorra.maplang --render mapa.png", options: { color: GREEN } },
  ], {
    x: 0.6, y: 4.65, w: 11.5, h: 0.5, fontFace: "Consolas", fontSize: 15,
    fill: { color: "0D0D0F" }, align: "left",
  });

  const demoSteps = [
    { n: "1", t: "Válida", d: "Mazmorra_del_Dragon (4 salas, 3 conexiones)" },
    { n: "2", t: "Válida", d: "Cripta_Olvidada (grilla 3×3, 7 salas)" },
    { n: "3", t: "Inválida", d: "Mapa_Roto → 3 errores sintácticos reportados" },
  ];
  let x = 0.6;
  demoSteps.forEach((d, i) => {
    let w = 3.65;
    let color = d.t === "Inválida" ? RED : GREEN;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 5.35, w, h: 1.55, rectRadius: 0.07, fill: { color: BG_DARK2 }, line: { color, width: 1 },
    });
    s.addText(`Caso ${d.n} — ${d.t}`, { x: x + 0.25, y: 5.48, w: w - 0.5, h: 0.4, fontFace: FONT_HEAD, fontSize: 14, bold: true, color });
    s.addText(d.d, { x: x + 0.25, y: 5.9, w: w - 0.5, h: 0.85, fontFace: FONT_BODY, fontSize: 12.5, color: WHITE, valign: "top" });
    x += w + 0.27;
  });

  pageNum(s, 10);
}

// =================================================================
// SLIDE 11 — Casos de prueba y resultados
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "05 · Casos de prueba");
  title(s, "14 casos · 52 pruebas automatizadas");

  // Stat callouts
  const stats = [
    { n: "8", l: "casos válidos", color: GREEN },
    { n: "6", l: "casos inválidos", color: RED },
    { n: "52", l: "pruebas unitarias", color: GOLD },
    { n: "100%", l: "resultado OK", color: BLUE },
  ];
  let w = 2.7, gap = 0.27, x0 = 0.6;
  stats.forEach((st, i) => {
    let x = x0 + i * (w + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: 2.05, w, h: 1.7, rectRadius: 0.08, fill: { color: BG_DARK2 }, line: { color: st.color, width: 1 },
    });
    s.addText(st.n, { x, y: 2.15, w, h: 0.95, align: "center", fontFace: FONT_HEAD, fontSize: 40, bold: true, color: st.color });
    s.addText(st.l, { x, y: 3.1, w, h: 0.5, align: "center", fontFace: FONT_BODY, fontSize: 13, color: WHITE });
  });

  let tableRows = [
    [
      { text: "Archivo", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
      { text: "Cobertura", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
      { text: "N.", options: { bold: true, color: GOLD, fill: { color: BG_DARK2 } } },
    ],
    [{ text: "test_lexer.py", options: { fontFace: "Consolas", color: WHITE } }, { text: "Tokens, errores léxicos", options: { color: GRAY } }, { text: "20", options: { color: WHITE, align: "center" } }],
    [{ text: "test_parser.py", options: { fontFace: "Consolas", color: WHITE } }, { text: "Producciones, recuperación, no-ambigüedad", options: { color: GRAY, fontSize: 11.5 } }, { text: "18", options: { color: WHITE, align: "center" } }],
    [{ text: "test_semantic.py", options: { fontFace: "Consolas", color: WHITE } }, { text: "Reglas S1–S4", options: { color: GRAY } }, { text: "10", options: { color: WHITE, align: "center" } }],
    [{ text: "test_integration.py", options: { fontFace: "Consolas", color: WHITE } }, { text: "Pipeline end-to-end + render", options: { color: GRAY } }, { text: "4", options: { color: WHITE, align: "center" } }],
  ];
  s.addTable(tableRows, {
    x: 0.6, y: 4.1, w: 11.5, h: 2.3,
    colW: [3.2, 6.8, 1.5],
    fontSize: 13, fontFace: FONT_BODY,
    border: { type: "solid", color: BG_DARK2, pt: 1 },
    fill: { color: BG_DARK }, valign: "middle", rowH: 0.46,
  });
  pageNum(s, 11);
}

// =================================================================
// SLIDE 12 — Discusión: dificultades y extensiones
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "06 · Discusión y aprendizajes");
  title(s, "Dificultades y posibles extensiones");

  s.addText("Dificultades encontradas", { x: 0.6, y: 2.0, w: 5.6, h: 0.4, fontFace: FONT_HEAD, fontSize: 17, bold: true, color: RED });
  s.addText([
    { text: "Evitar ambigüedad en <atributo>", options: { bold: true, breakLine: true, color: WHITE } },
    { text: "→ resuelto con keywords distintivas por atributo.", options: { breakLine: true, color: GRAY } },
    { text: " ", options: { breakLine: true } },
    { text: "Estrategia de recuperación de errores", options: { bold: true, breakLine: true, color: WHITE } },
    { text: "→ sincronización en modo pánico hacia ROOM/CONNECT/'}'.", options: { color: GRAY } },
  ], { x: 0.6, y: 2.5, w: 5.6, h: 3.6, fontFace: FONT_BODY, fontSize: 14, valign: "top", lineSpacing: 22 });

  s.addText("Extensiones futuras", { x: 6.85, y: 2.0, w: 5.6, h: 0.4, fontFace: FONT_HEAD, fontSize: 17, bold: true, color: GREEN });
  s.addText([
    { text: "<evento> anidado en <sala>", options: { bullet: true, breakLine: true, color: WHITE } },
    { text: "(lógica de triggers, sin romper LL(1))", options: { breakLine: true, color: GRAY, fontSize: 12.5 } },
    { text: "Análisis de alcanzabilidad", options: { bullet: true, breakLine: true, color: WHITE } },
    { text: "(verificar que todas las salas sean alcanzables desde la entrada)", options: { color: GRAY, fontSize: 12.5 } },
  ], { x: 6.85, y: 2.5, w: 5.6, h: 3.6, fontFace: FONT_BODY, fontSize: 14, valign: "top", lineSpacing: 22 });

  pageNum(s, 12);
}

// =================================================================
// SLIDE 13 — Conclusiones (≈3 min)
// =================================================================
{
  let s = pres.addSlide();
  bgSlide(s);
  kicker(s, "07 · Conclusiones");
  title(s, "Lo que aprendimos como equipo");

  const concl = [
    "Gramática GLC de 20 producciones: libre de contexto, no ambigua y LL(1)",
    "Lexer y parser manuales, con recuperación de errores en una sola pasada",
    "AST tipado + validación semántica + renderizado visual del mapa",
    "52 pruebas automatizadas y 14 casos documentados, todos OK",
    "Fijar decisiones gramaticales (keywords distintivas) temprano evita retrabajo costoso",
  ];
  s.addText(concl.map(t => ({ text: t, options: { bullet: { code: "27A4" }, breakLine: true, color: WHITE } })), {
    x: 0.6, y: 2.15, w: 11.5, h: 3.6, fontFace: FONT_BODY, fontSize: 17, valign: "top", lineSpacing: 38,
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 6.15, w: 11.5, h: 0.02, fill: { color: BG_DARK2 }, line: { type: "none" } });
  s.addText("¡Gracias! Preguntas.", {
    x: 0.6, y: 6.35, w: 11.5, h: 0.6, fontFace: FONT_HEAD, fontSize: 22, bold: true, color: GOLD, align: "center",
  });
  pageNum(s, 13);
}

pres.writeFile({ fileName: "MapLang_Presentacion.pptx" }).then(() => {
  console.log("Presentación generada: MapLang_Presentacion.pptx");
});
