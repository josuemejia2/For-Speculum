const views = document.querySelectorAll(".lab-view");
const tabs = document.querySelectorAll(".lab-tab");
const $ = (selector) => document.querySelector(selector);

const custodyRules = {
  urgencia: ["ya", "ahora", "rapido", "urgente", "no puedo esperar"],
  miedo: ["miedo", "perder", "pierdo", "perdi", "panico", "ansiedad"],
  euforia: ["seguro", "100%", "facil", "garantizado", "all in"],
  venganza: ["recuperar", "venganza", "desquito", "doblar", "meter mas"],
  disciplina: ["esperar", "confirmar", "bitacora", "validar", "no operar", "backup"],
};

const trialDeck = [
  {
    text: "El precio se mueve rapido y sientes que si no entras ya pierdes la oportunidad.",
    answer: "esperar",
    stat: "custodia",
    why: "Urgencia no es senal. Primero se detiene y se verifica.",
  },
  {
    text: "Tienes una regla nueva, pero todavia no aparece en bitacora ni tiene repeticiones.",
    answer: "registrar",
    stat: "evidencia",
    why: "Sin registro no hay evidencia operativa.",
  },
  {
    text: "Un documento editado por IA parece completo, pero no lo comparaste contra la base.",
    answer: "verificar",
    stat: "disciplina",
    why: "QUERO.OS exige verificar antes de guardar.",
  },
  {
    text: "Hay vela valida, contexto, volumen, regla clara e invalidacion definida.",
    answer: "operar",
    stat: "disciplina",
    why: "La accion puede existir cuando la condicion esta completa.",
  },
  {
    text: "Quieres recuperar una perdida aumentando tamano sin plan previo.",
    answer: "esperar",
    stat: "custodia",
    why: "Recuperar por impulso activa ruido estructural.",
  },
];

let trialIndex = 0;
let trialCorrect = 0;
let trialTotal = 0;
const stats = {
  disciplina: 0,
  evidencia: 0,
  custodia: 0,
  ruido: 0,
};

function setView(name) {
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === name));
  views.forEach((view) => view.classList.toggle("active", view.id === `${name}-view`));
  if (name === "nodo") resizeNodoCanvas();
}

tabs.forEach((tab) => tab.addEventListener("click", () => setView(tab.dataset.view)));

function scanCustody(text) {
  const normalized = text.toLowerCase();
  const hits = {};
  let noise = 0;
  let discipline = 0;

  Object.entries(custodyRules).forEach(([key, words]) => {
    const found = words.filter((word) => normalized.includes(word));
    hits[key] = found;
    if (!found.length) return;
    if (key === "disciplina") discipline += found.length;
    else noise += found.length;
  });

  if (noise > 0) {
    return {
      state: "Custodia activa",
      level: Math.min(100, 35 + noise * 18),
      hits,
      action: "Pausar. Registrar. No ejecutar por impulso.",
    };
  }
  if (discipline > 0) {
    return {
      state: "Disciplina",
      level: 18,
      hits,
      action: "Puede pasar a verificacion.",
    };
  }
  return {
    state: "Neutral",
    level: 28,
    hits,
    action: "Falta evidencia. Pedir contexto.",
  };
}

function renderCustody(result) {
  const badge = $("#custody-badge");
  const state = $("#custody-state");
  const output = $("#custody-output");
  const fill = $("#noise-fill");
  const signals = Object.entries(result.hits)
    .filter(([, words]) => words.length)
    .map(([key, words]) => `${key}: ${words.join(", ")}`);

  badge.textContent = result.state;
  state.textContent = result.state;
  fill.style.width = `${result.level}%`;
  output.innerHTML = `
    <strong>${result.state}</strong><br>
    Senales: ${signals.length ? signals.join(" - ") : "sin senales fuertes"}<br>
    Accion: ${result.action}
  `;
}

$("#custody-analyze").addEventListener("click", () => {
  const text = $("#custody-input").value.trim();
  renderCustody(scanCustody(text));
});

$("#custody-sample").addEventListener("click", () => {
  const samples = [
    "Quiero entrar ya para recuperar rapido.",
    "Voy a esperar confirmacion y registrar en bitacora.",
    "Esto es 100% seguro, meto mas.",
  ];
  const input = $("#custody-input");
  input.value = samples[Math.floor(Math.random() * samples.length)];
  renderCustody(scanCustody(input.value));
});

const canvas = $("#nodo-canvas");
const ctx = canvas.getContext("2d");
const sensorGrid = $("#sensor-grid");
const sequenceGrid = $("#sequence-grid");
const sourceButton = $("#nodo-source");
const apiButton = $("#nodo-api");
const pauseButton = $("#nodo-pause");
const timeframeButtons = document.querySelectorAll("[data-timeframe]");
const timeframeStatus = $("#timeframe-status");

const sensorLabels = [
  ["EMA 3/9", "Corte rapido"],
  ["EMA 9/20", "Tendencia"],
  ["EMA 20/50", "Estructura"],
  ["EMA 50/200", "Macro"],
  ["MACD", "Momentum"],
  ["Bandas BB", "Volatilidad"],
  ["PSAR", "Rotacion"],
  ["Vela actual", "Estructura"],
];

const chartTimeframes = [
  { label: "1m", minutes: 1, step: 1 },
  { label: "5m", minutes: 5, step: 5 },
  { label: "15m", minutes: 15, step: 15 },
  { label: "1h", minutes: 60, step: 60 },
];

const historyLimit = 3600;

const market = {
  points: [],
  tick: 0,
  paused: false,
  source: "SIMULADO",
  lastTickAt: 0,
  snapshot: null,
  bandAlert: null,
  timeframe: "1m",
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function standardDeviation(values) {
  const avg = average(values);
  const variance = average(values.map((value) => (value - avg) ** 2));
  return Math.sqrt(variance);
}

function ema(values, period) {
  const multiplier = 2 / (period + 1);
  const result = [];
  let previous = values[0] || 0;
  values.forEach((value, index) => {
    previous = index === 0 ? value : value * multiplier + previous * (1 - multiplier);
    result.push(previous);
  });
  return result;
}

function buildCandles(points) {
  return points.map((close, index) => {
    const open = index > 0 ? points[index - 1] : close;
    const body = Math.abs(close - open);
    const wick = Math.max(body * 0.18, Math.abs(close) * 0.0008, 0.04);
    return {
      open,
      close,
      high: Math.max(open, close) + wick,
      low: Math.min(open, close) - wick,
    };
  });
}

function syntheticPriceAt(index) {
  const trend = index * 0.025;
  const majorWave = Math.sin(index * 0.087) * 6.1;
  const secondaryWave = Math.sin(index * 0.168 + 1.2) * 2.2;
  const slowBias = Math.sin(index * 0.026 - 0.7) * 2.8;
  return 106.8 + trend + majorWave + secondaryWave + slowBias;
}

function seedMarket(seedPoints = null) {
  market.points = [];
  market.tick = 0;
  market.bandAlert = null;
  if (seedPoints?.length) {
    market.points = seedPoints.slice(-historyLimit);
    market.tick = market.points.length;
    market.source = "API + SIM";
    sourceButton.textContent = market.source;
    return;
  }

  for (let i = 0; i < historyLimit; i += 1) {
    const price = syntheticPriceAt(i) + (Math.random() - 0.5) * 0.72;
    market.points.push(price);
  }
  market.tick = market.points.length;
  market.source = "SIMULADO";
  sourceButton.textContent = market.source;
}

function pushSimPoint() {
  const last = market.points[market.points.length - 1] || 112;
  const t = market.tick;
  const recent = market.points.slice(-60);
  const avg = average(recent);
  const scale = Math.max(0.18, Math.abs(avg || last) * 0.0024);
  const target = market.source === "SIMULADO" ? syntheticPriceAt(t) : avg || last;
  const pressure = (target - last) * (market.source === "SIMULADO" ? 0.18 : 0.025);
  const wave = Math.sin(t * 0.19) * scale + Math.sin(t * 0.047) * scale * 0.8;
  const noise = (Math.random() - 0.5) * scale * 1.1;
  const next = Math.max(0.01, last + pressure + wave + noise);
  market.points.push(next);
  if (market.points.length > historyLimit) market.points.shift();
  market.tick += 1;
}

function formatPrice(value) {
  return Number.isFinite(value) ? value.toFixed(2) : "0.00";
}

function sensorState(value, neutral = 0.08) {
  if (value > neutral) return { label: "Alcista", className: "good" };
  if (value < -neutral) return { label: "Bajista", className: "danger" };
  return { label: "Mixta", className: "mixed" };
}

function currentTimeframe() {
  return chartTimeframes.find((frame) => frame.label === market.timeframe) || chartTimeframes[0];
}

function syncTimeframeControls(chartWorld = null) {
  const frame = currentTimeframe();
  timeframeButtons.forEach((button) => {
    const active = button.dataset.timeframe === frame.label;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  if (timeframeStatus) {
    const count = chartWorld?.points?.length || aggregateTimeframeCloses(market.points, frame.step).length;
    timeframeStatus.textContent = `Mundo activo ${frame.label} - ${count} velas - EMA20/50 recalculada`;
  }
}

function selectTimeframe(timeframe) {
  if (!chartTimeframes.some((frame) => frame.label === timeframe)) return;
  market.timeframe = timeframe;
  syncTimeframeControls();
  if (market.snapshot) {
    renderNodes(market.snapshot);
    drawMarketChart(market.snapshot, performance.now());
  }
}

function aggregateTimeframeCloses(values, step) {
  if (step <= 1) return values.slice();
  const series = [];
  for (let end = values.length; end > 0; end -= step) {
    series.unshift(values[end - 1]);
  }
  return series;
}

function formatMinutesBack(minutes) {
  if (minutes <= 0) return "ahora";
  if (minutes < 60) return `-${minutes}m`;
  const hours = minutes / 60;
  return Number.isInteger(hours) ? `-${hours}h` : `-${hours.toFixed(1)}h`;
}

function comparePriceToEMA20(price, ema20Value, sequenceDirection = "NONE") {
  const tolerance = Math.max(Math.abs(ema20Value) * 0.0005, 0.0001);
  let direction = "neutral";
  if (price > ema20Value + tolerance) direction = "positive";
  if (price < ema20Value - tolerance) direction = "negative";

  const confirmedLong = direction === "positive";
  const confirmedShort = direction === "negative";
  const normalizedDirection = String(sequenceDirection || "NONE").toUpperCase();
  const validatesSequence =
    (normalizedDirection === "LONG" && confirmedLong) ||
    (normalizedDirection === "SHORT" && confirmedShort);

  return {
    direction,
    confirmedLong,
    confirmedShort,
    validatesSequence,
    sequenceDirection: normalizedDirection,
    price,
    ema20: ema20Value,
  };
}

function detectSmartCandle(candle, averages) {
  const bodyLow = Math.min(candle.open, candle.close);
  const bodyHigh = Math.max(candle.open, candle.close);
  const bodyCrosses = averages.filter((level) => level >= bodyLow && level <= bodyHigh).length;
  const rangeCrosses = averages.filter((level) => level >= candle.low && level <= candle.high).length;
  const aboveCount = averages.filter((level) => candle.close > level).length;
  const belowCount = averages.filter((level) => candle.close < level).length;
  const crosses = Math.max(bodyCrosses, rangeCrosses);
  const positiveBody = candle.close > candle.open;
  const negativeBody = candle.close < candle.open;

  return {
    positive: {
      passed: positiveBody && (crosses >= 3 || aboveCount >= 3),
      detail: `Cruza ${crosses}/5 - arriba ${aboveCount}/5`,
    },
    negative: {
      passed: negativeBody && (crosses >= 3 || belowCount >= 3),
      detail: `Cruza ${crosses}/5 - abajo ${belowCount}/5`,
    },
  };
}

function parabolicSar(candles, step = 0.02, maxStep = 0.2) {
  if (candles.length < 2) return candles.map((candle) => candle.close);
  const result = Array(candles.length).fill(candles[0].close);
  let rising = candles[1].close >= candles[0].close;
  let acceleration = step;
  let extreme = rising ? candles[1].high : candles[1].low;
  let sar = rising ? candles[0].low : candles[0].high;
  result[0] = sar;
  result[1] = sar;

  for (let index = 2; index < candles.length; index += 1) {
    const candle = candles[index];
    sar += acceleration * (extreme - sar);
    if (rising) {
      sar = Math.min(sar, candles[index - 1].low, candles[index - 2].low);
      if (candle.low < sar) {
        rising = false;
        sar = extreme;
        extreme = candle.low;
        acceleration = step;
      } else if (candle.high > extreme) {
        extreme = candle.high;
        acceleration = Math.min(maxStep, acceleration + step);
      }
    } else {
      sar = Math.max(sar, candles[index - 1].high, candles[index - 2].high);
      if (candle.high > sar) {
        rising = true;
        sar = extreme;
        extreme = candle.high;
        acceleration = step;
      } else if (candle.low < extreme) {
        extreme = candle.low;
        acceleration = Math.min(maxStep, acceleration + step);
      }
    }
    result[index] = sar;
  }
  return result;
}

function buildBandDestinationAlert({
  ema39Signal,
  ema20Sensor,
  macdSlope,
  psarSignal,
  smartCandle,
  candle,
  upperBand,
  lowerBand,
  forcedDirection = null,
}) {
  const slopeNeutral = 0.006;
  let direction = forcedDirection || "neutral";
  if (!forcedDirection) {
    if (macdSlope > slopeNeutral) direction = "positive";
    if (macdSlope < -slopeNeutral) direction = "negative";
  }

  const isPositive = direction === "positive";
  const isNegative = direction === "negative";
  const className = isNegative ? "danger" : isPositive ? "good" : "mixed";
  const smartGate = isNegative ? smartCandle.negative : smartCandle.positive;
  const targetBand = isPositive ? upperBand : isNegative ? lowerBand : null;
  const targetName = isPositive ? "Banda superior" : isNegative ? "Banda inferior" : "Banda en espera";
  const bandTouched = isPositive ? candle.high >= upperBand : isNegative ? candle.low <= lowerBand : false;

  const items = [
    {
      label: "EMA 3/9",
      detail: isNegative ? "EMA3 < EMA9" : "EMA3 > EMA9",
      passed: isPositive ? ema39Signal > 0 : isNegative ? ema39Signal < 0 : false,
    },
    {
      label: isNegative ? "Precio bajo EMA20" : "Precio sobre EMA20",
      detail: "Centro del sistema",
      passed: isPositive ? ema20Sensor.confirmedLong : isNegative ? ema20Sensor.confirmedShort : false,
    },
    {
      label: isNegative ? "MACD bajando" : "MACD subiendo",
      detail: `Pendiente ${macdSlope >= 0 ? "+" : ""}${macdSlope.toFixed(3)}`,
      passed: isPositive || isNegative,
    },
    {
      label: isNegative ? "Parabolica negativa" : "Parabolica positiva",
      detail: isNegative ? "PSAR arriba" : "PSAR debajo",
      passed: isPositive ? psarSignal > 0 : isNegative ? psarSignal < 0 : false,
    },
    {
      label: "Vela Inteligente",
      detail: smartGate.detail,
      passed: (isPositive || isNegative) && smartGate.passed,
      gate: true,
    },
  ];

  const baseReady = items.slice(0, 4).every((item) => item.passed);
  const activated = baseReady && items[4].passed;
  const fulfilled = activated && bandTouched;
  const confirmations = items.filter((item) => item.passed).length;
  const sequenceDirection = isPositive ? "LONG" : isNegative ? "SHORT" : "NONE";
  const status = fulfilled ? "fulfilled" : activated ? "active" : baseReady ? "armed" : "waiting";
  const distanceToBand = targetBand === null ? 0 : Math.abs(targetBand - candle.close);

  return {
    direction,
    sequenceDirection,
    className,
    title: isPositive ? "ALERTA ALCISTA" : isNegative ? "ALERTA BAJISTA" : "TRANSICION NEUTRAL",
    probability: 87,
    targetBand,
    targetName,
    bandTouched,
    baseReady,
    activated,
    fulfilled,
    confirmations,
    status,
    distanceToBand,
    items,
  };
}

function updateBandAlertLifecycle(alert, candle, tick) {
  if (market.bandAlert?.status === "fulfilled" && tick - market.bandAlert.fulfilledAt > 24) {
    market.bandAlert = null;
  }

  if (market.bandAlert?.status === "active") {
    const live = market.bandAlert;
    const touched = live.direction === "positive" ? candle.high >= live.targetBand : candle.low <= live.targetBand;
    if (touched) {
      market.bandAlert = {
        ...live,
        status: "fulfilled",
        fulfilledAt: tick,
      };
    }
  }

  if (!market.bandAlert && alert.activated) {
    market.bandAlert = {
      status: "active",
      direction: alert.direction,
      className: alert.className,
      targetBand: alert.targetBand,
      targetName: alert.targetName,
      probability: alert.probability,
      createdAt: tick,
    };
  }

  if (!market.bandAlert) return alert;

  const live = market.bandAlert;
  const fulfilled = live.status === "fulfilled";
  return {
    ...alert,
    direction: live.direction,
    sequenceDirection: live.direction === "positive" ? "LONG" : "SHORT",
    className: live.className,
    title: live.direction === "positive" ? "ALERTA ALCISTA" : "ALERTA BAJISTA",
    targetBand: live.targetBand,
    targetName: live.targetName,
    probability: live.probability,
    bandTouched: fulfilled || alert.bandTouched,
    activated: !fulfilled,
    fulfilled,
    status: live.status,
    persistent: true,
    createdAt: live.createdAt,
    fulfilledAt: live.fulfilledAt,
    distanceToBand: Math.abs(live.targetBand - candle.close),
  };
}

function crossedLevel(previous, current, level, tolerance) {
  return Math.abs(current - level) <= tolerance || (previous < level && current > level) || (previous > level && current < level);
}

function findReturnIndex(points, startIndex, level) {
  const tolerance = Math.max(Math.abs(level) * 0.006, 0.18);
  let movedAway = false;
  for (let index = Math.ceil(startIndex) + 1; index < points.length; index += 1) {
    if (!movedAway) {
      movedAway = Math.abs(points[index] - level) > tolerance * 1.8;
      continue;
    }
    if (crossedLevel(points[index - 1], points[index], level, tolerance)) {
      return index;
    }
  }
  return null;
}

function interpolateCross(index, ema20, ema50) {
  const previousDiff = ema20[index - 1] - ema50[index - 1];
  const currentDiff = ema20[index] - ema50[index];
  const denominator = Math.abs(previousDiff) + Math.abs(currentDiff);
  const ratio = denominator > 0 ? Math.abs(previousDiff) / denominator : 0;
  const crossIndex = index - 1 + ratio;
  const ema20Level = ema20[index - 1] + (ema20[index] - ema20[index - 1]) * ratio;
  const ema50Level = ema50[index - 1] + (ema50[index] - ema50[index - 1]) * ratio;
  return {
    index: crossIndex,
    level: (ema20Level + ema50Level) / 2,
  };
}

function detectQueroLines(points, ema20, ema50) {
  const lines = [];
  for (let index = 3; index < points.length; index += 1) {
    const before = ema20[index - 1] - ema50[index - 1];
    const after = ema20[index] - ema50[index];
    const hasCross = (before <= 0 && after > 0) || (before >= 0 && after < 0);
    if (!hasCross) continue;

    const positiveCross = before <= 0 && after > 0;
    const polarity = positiveCross ? "negative" : "positive";
    const color = polarity === "positive" ? "#00d57e" : "#ff4048";
    const cross = interpolateCross(index, ema20, ema50);
    const level = cross.level;
    const returnIndex = findReturnIndex(points, cross.index, level);
    lines.push({
      id: `${index}-${polarity}`,
      startIndex: cross.index,
      endIndex: returnIndex ?? points.length - 1,
      level,
      polarity,
      color,
      completed: returnIndex !== null,
      crossLabel: positiveCross ? "Cruce positivo EMA20/50" : "Cruce negativo EMA20/50",
      lineLabel: polarity === "positive" ? "Positiva" : "Negativa",
    });
  }
  return lines;
}

function fallbackTimeframeLine(points, polarity) {
  const window = points.slice(-Math.min(points.length, 90));
  const fallbackLevel = window.length
    ? (polarity === "positive" ? Math.min(...window) : Math.max(...window))
    : 0;
  return {
    startIndex: Math.max(0, points.length - 55),
    endIndex: Math.max(0, points.length - 1),
    level: fallbackLevel,
    polarity,
    color: polarity === "positive" ? "#00d57e" : "#ff4048",
    completed: false,
    crossLabel: "Sin cruce EMA20/50 en este timeframe",
    lineLabel: polarity === "positive" ? "Positiva" : "Negativa",
  };
}

function buildTimeframeWorld(points, frame) {
  const timeframePoints = aggregateTimeframeCloses(points, frame.step);
  const ema20Frame = ema(timeframePoints, 20);
  const ema50Frame = ema(timeframePoints, 50);
  const queroLines = detectQueroLines(timeframePoints, ema20Frame, ema50Frame);
  const positiveLines = queroLines.filter((line) => line.polarity === "positive");
  const negativeLines = queroLines.filter((line) => line.polarity === "negative");
  return {
    frame,
    points: timeframePoints,
    ema20: ema20Frame,
    ema50: ema50Frame,
    queroLines,
    nodeOne: positiveLines.at(-1) || fallbackTimeframeLine(timeframePoints, "positive"),
    nodeTwo: negativeLines.at(-1) || fallbackTimeframeLine(timeframePoints, "negative"),
  };
}

function buildSnapshot() {
  const points = market.points;
  const candles = buildCandles(points);
  const ema3 = ema(points, 3);
  const ema9 = ema(points, 9);
  const ema20 = ema(points, 20);
  const ema50 = ema(points, 50);
  const ema200 = ema(points, 120);
  const psar = parabolicSar(candles);
  const last = points.at(-1);
  const previous = points.at(-2) || last;
  const delta = last - previous;
  const recent = points.slice(-20);
  const recentAvg = average(recent);
  const bbDeviation = standardDeviation(recent);
  const upperBand = recentAvg + bbDeviation * 2;
  const lowerBand = recentAvg - bbDeviation * 2;
  const bbWidth = recentAvg ? (bbDeviation / recentAvg) * 100 : 0;
  const macd = ema3.at(-1) - ema9.at(-1);
  const macdAxis = ema3.at(-1) - ema9.at(-1);
  const previousMacdAxis = (ema3.at(-2) || ema3.at(-1)) - (ema9.at(-2) || ema9.at(-1));
  const macdSlope = macdAxis - previousMacdAxis;
  const bandSignal = bbWidth > 1.35 ? (last >= recentAvg ? 1 : -1) : 0;
  const psarSignal = last - psar.at(-1);
  const smartCandle = detectSmartCandle(candles.at(-1), [
    ema3.at(-1),
    ema9.at(-1),
    ema20.at(-1),
    ema50.at(-1),
    ema200.at(-1),
  ]);
  const slope20 = ema20.at(-1) - (ema20.at(-6) || ema20.at(-1));
  const slope50 = ema50.at(-1) - (ema50.at(-8) || ema50.at(-1));

  const rawSensors = [
    ema3.at(-1) - ema9.at(-1),
    ema9.at(-1) - ema20.at(-1),
    ema20.at(-1) - ema50.at(-1),
    ema50.at(-1) - ema200.at(-1),
    macd,
    bandSignal,
    psarSignal,
    delta,
  ];

  const sensors = rawSensors.map((value, index) => {
    const state = sensorState(value, index === 5 ? 0.18 : 0.06);
    const metric = index === 5 ? `BW ${bbWidth.toFixed(2)}` : `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
    return {
      index: index + 1,
      label: sensorLabels[index][0],
      detail: sensorLabels[index][1],
      metric,
      value,
      ...state,
    };
  });

  const good = sensors.filter((sensor) => sensor.className === "good").length;
  const mixed = sensors.filter((sensor) => sensor.className === "mixed").length;
  const score = Math.round(((good + mixed * 0.5) / sensors.length) * 100);
  const regime = score >= 63 ? "alcista" : score <= 37 ? "bajista" : "mixto";
  const direction = regime === "alcista" ? 1 : regime === "bajista" ? -1 : 0;
  const queroLines = detectQueroLines(points, ema20, ema50);
  const latestLine = queroLines.at(-1) || null;
  const ema20Sensor = comparePriceToEMA20(last, ema20.at(-1));
  const forcedAlertDirection = market.bandAlert?.direction || null;
  const bandAlertCandidate = buildBandDestinationAlert({
    ema39Signal: ema3.at(-1) - ema9.at(-1),
    ema20Sensor,
    macdSlope,
    psarSignal,
    smartCandle,
    candle: candles.at(-1),
    upperBand,
    lowerBand,
    forcedDirection: forcedAlertDirection,
  });
  const bandAlert = updateBandAlertLifecycle(bandAlertCandidate, candles.at(-1), market.tick);
  const sequenceDirection = bandAlert.sequenceDirection;
  const sequence = bandAlert.items.map((item) => item.passed);
  const positiveLines = queroLines.filter((line) => line.polarity === "positive");
  const negativeLines = queroLines.filter((line) => line.polarity === "negative");
  const fallbackPositive = {
    startIndex: Math.max(12, points.length - 95),
    endIndex: Math.max(16, points.length - 55),
    level: Math.min(...points.slice(-120, -35)),
    polarity: "positive",
    color: "#00d57e",
    completed: true,
    crossLabel: "Cruce negativo EMA20/50",
    lineLabel: "Positiva",
  };
  const fallbackNegative = {
    startIndex: Math.max(18, points.length - 70),
    endIndex: points.length - 1,
    level: Math.max(...points.slice(-90)),
    polarity: "negative",
    color: "#ff4048",
    completed: false,
    crossLabel: "Cruce positivo EMA20/50",
    lineLabel: "Negativa",
  };
  const nodeOne = positiveLines.at(-1) || fallbackPositive;
  const nodeTwo = negativeLines.at(-1) || fallbackNegative;

  return {
    points,
    ema9,
    ema20,
    ema50,
    last,
    previous,
    delta,
    sensors,
    score,
    good,
    mixed,
    regime,
    direction,
    sequence,
    sequenceDirection,
    ema20Sensor,
    bandAlert,
    nodeOne,
    nodeTwo,
    queroLines,
    latestLine,
    slope20,
    slope50,
  };
}

function renderSensors(snapshot) {
  sensorGrid.innerHTML = snapshot.sensors
    .map((sensor) => `
      <article class="sensor-card ${sensor.className}">
        <div class="sensor-top"><span class="sensor-index">${sensor.index}</span>${sensor.label}</div>
        <strong class="sensor-state">${sensor.label === "Bandas BB" && sensor.className !== "mixed" ? "Expansion" : sensor.label}</strong>
        <span class="sensor-detail">${sensor.detail}</span>
        <span class="sensor-value">${sensor.metric}</span>
      </article>
    `)
    .join("");
}

function renderThermo(snapshot) {
  const score = clamp(snapshot.score, 0, 100);
  $("#score-confirmations").textContent = `${snapshot.good} / 8`;
  $("#score-value").textContent = `${score}%`;
  $("#score-regime").textContent = snapshot.regime;
  $("#thermo-fill").style.width = `${score}%`;
  $("#thermo-marker").style.left = `${score}%`;
  $("#thermo-marker").textContent = `${score}%`;

  const dots = Array.from({ length: 15 }, (_, index) => {
    const value = Math.round((index / 14) * 100);
    const active = value <= score;
    const className = value < 38 ? "danger" : value < 63 ? "mixed" : "good";
    return `<span class="thermo-dot ${active ? className : ""}"></span>`;
  });
  $("#thermo-dots").innerHTML = dots.join("");
}

function renderNodes(snapshot) {
  const chartWorld = buildTimeframeWorld(snapshot.points, currentTimeframe());
  syncTimeframeControls(chartWorld);
  const positiveState = chartWorld.nodeOne.completed ? "cerrada en Punto B" : "pendiente de regreso";
  const negativeState = chartWorld.nodeTwo.completed ? "cerrada en Punto B" : "pendiente de regreso";
  $("#node-one").innerHTML = `
    <span>Linea positiva ${chartWorld.frame.label}</span>
    <strong>${formatPrice(chartWorld.nodeOne.level)}</strong>
    <small>${chartWorld.nodeOne.crossLabel} - ${positiveState}</small>
  `;
  $("#node-two").innerHTML = `
    <span>Linea negativa ${chartWorld.frame.label}</span>
    <strong>${formatPrice(chartWorld.nodeTwo.level)}</strong>
    <small>${chartWorld.nodeTwo.crossLabel} - ${negativeState}</small>
  `;
}

function renderAlertChecklist(alert) {
  const rows = alert.items
    .map((item) => `
      <li class="sequence-step ${item.passed ? "on" : "off"}">
        <span class="step-mark">${item.passed ? "SI" : item.gate && alert.baseReady ? "GAT" : "--"}</span>
        <span>
          <b>${item.label}</b>
          <small>${item.detail}</small>
        </span>
      </li>
    `)
    .join("");
  return `
    <article class="sequence-branch ${alert.className} active">
      <div class="sequence-branch-title">
        <span>Sensor nuevo</span>
        <strong>${alert.title}</strong>
      </div>
      <ul class="sequence-steps">${rows}</ul>
      <div class="sequence-branch-result">${alert.confirmations}/5 condiciones</div>
    </article>
  `;
}

function renderAlertDestination(alert) {
  const target = alert.targetBand === null ? "0.00" : formatPrice(alert.targetBand);
  const distance = alert.targetBand === null ? "0.00" : formatPrice(alert.distanceToBand);
  const rows = [
    ["Probabilidad", alert.activated || alert.fulfilled ? "87%" : "Pendiente", alert.activated || alert.fulfilled],
    ["Destino", `${alert.targetName} ${target}`, alert.activated],
    ["Distancia", distance, alert.activated],
    ["Toque de banda", alert.bandTouched ? "Cumplido" : "Pendiente", alert.fulfilled],
  ]
    .map(([label, detail, passed]) => `
      <li class="sequence-step ${passed ? "on" : "off"}">
        <span class="step-mark">${passed ? "OK" : "--"}</span>
        <span>
          <b>${label}</b>
          <small>${detail}</small>
        </span>
      </li>
    `)
    .join("");
  return `
    <article class="sequence-branch ${alert.className} ${alert.activated ? "active" : ""}">
      <div class="sequence-branch-title">
        <span>Destino</span>
        <strong>Banda 87%</strong>
      </div>
      <ul class="sequence-steps">${rows}</ul>
      <div class="sequence-branch-result">${alert.fulfilled ? "CUMPLIDA" : alert.activated ? "ACTIVA" : "PENDIENTE"}</div>
    </article>
  `;
}

function renderSequence(snapshot) {
  const alert = snapshot.bandAlert;
  sequenceGrid.innerHTML = `
    ${renderAlertChecklist(alert)}
    ${renderAlertDestination(alert)}
  `;

  const status = $(".sequence-status");
  status.classList.remove("bullish", "bearish", "mixed");
  if (alert.fulfilled) {
    status.classList.add(alert.direction === "negative" ? "bearish" : "bullish");
    $("#sequence-title").textContent = "ALERTA CUMPLIDA";
    $("#sequence-copy").textContent = `El precio toco la ${alert.targetName.toLowerCase()} de Bollinger; el MACD acompano la direccion.`;
    $("#sequence-action").textContent = `BANDA CUMPLIDA - ${alert.probability}%`;
    return;
  }
  if (alert.activated) {
    status.classList.add(alert.direction === "negative" ? "bearish" : "bullish");
    $("#sequence-title").textContent = "ALERTA ACTIVA";
    $("#sequence-copy").textContent = `Condiciones alineadas. Vela Inteligente activo el destino hacia la ${alert.targetName.toLowerCase()} de Bollinger con lectura ${alert.probability}%.`;
    $("#sequence-action").textContent = `${alert.targetName.toUpperCase()} - ${formatPrice(alert.targetBand)}`;
    return;
  }
  if (alert.baseReady) {
    status.classList.add(alert.direction === "negative" ? "bearish" : "bullish");
    $("#sequence-title").textContent = "ALERTA ARMADA";
    $("#sequence-copy").textContent = "3/9, EMA20, MACD y Parabolica estan listos. Falta Vela Inteligente para activar.";
    $("#sequence-action").textContent = "ESPERA VELA";
    return;
  }

  status.classList.add("mixed");
  $("#sequence-title").textContent = "TRANSICION NEUTRAL";
  $("#sequence-copy").textContent = "La alerta espera 3/9, precio sobre/bajo EMA20, MACD en direccion y Parabolica.";
  $("#sequence-action").textContent = `ESPERA - ${formatPrice(snapshot.last)}`;
}

function updateSystemStrip(snapshot) {
  $("#pulse-state").textContent = market.paused ? "Pausado" : "Moviendo";
  if ($("#nodo-view").classList.contains("active")) {
    $("#custody-state").textContent = snapshot.regime === "mixto" ? "Vigilante" : "Lectura activa";
  }
}

function resizeNodoCanvas() {
  if (!canvas) return null;
  const rect = canvas.getBoundingClientRect();
  if (!rect.width) return null;
  const cssWidth = Math.max(320, Math.floor(rect.width));
  const cssHeight = Math.max(260, Math.round(cssWidth * 0.42));
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(cssWidth * dpr) || canvas.height !== Math.round(cssHeight * dpr)) {
    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);
    canvas.style.height = `${cssHeight}px`;
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { width: cssWidth, height: cssHeight };
}

function drawLine(points, color, width, mapper) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.beginPath();
  points.forEach((point, index) => {
    const value = typeof point === "object" ? point.value : point;
    const axisIndex = typeof point === "object" ? point.offset : index;
    const [x, y] = mapper(value, axisIndex, index);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function roundRectPath(x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
}

function drawNode(marker, visibleStart, xForIndex, yForPrice, color, title, subtitle, pulse, size) {
  const index = marker.index - visibleStart;
  if (index < 0 || index > 131) return;
  const x = xForIndex(index);
  const y = yForPrice(marker.price);
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.setLineDash([9, 8]);
  ctx.beginPath();
  ctx.moveTo(48, y);
  ctx.lineTo(x, y);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(x, y, 8 + pulse, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "rgba(3, 7, 11, .9)";
  ctx.strokeStyle = color;
  const boxX = Math.min(Math.max(54, x + 16), Math.max(54, size.width - 210));
  const boxY = clamp(y - 46, 52, size.height - 86);
  ctx.lineWidth = 1.5;
  roundRectPath(boxX, boxY, 166, 58, 7);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = "700 12px Consolas, monospace";
  ctx.fillText(title, boxX + 12, boxY + 22);
  ctx.font = "900 18px Consolas, monospace";
  ctx.fillText(subtitle, boxX + 12, boxY + 45);
}

function drawPoint(x, y, color, filled, pulse = 0) {
  ctx.lineWidth = 4;
  ctx.strokeStyle = "#f2f5f6";
  ctx.fillStyle = filled ? color : "#ffffff";
  ctx.beginPath();
  ctx.arc(x, y, 10 + pulse, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.lineWidth = 3;
  ctx.strokeStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, 15 + pulse * 0.55, 0, Math.PI * 2);
  ctx.stroke();
}

function drawBadge(x, y, color, text, size) {
  const width = Math.max(152, text.length * 10 + 34);
  const height = 44;
  const boxX = clamp(x + 14, 62, size.width - width - 14);
  const boxY = clamp(y - 28, 50, size.height - 92);
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  roundRectPath(boxX, boxY, width, height, 8);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#071016";
  ctx.font = "900 18px Consolas, monospace";
  ctx.fillText(text, boxX + 16, boxY + 28);
}

function drawQueroLine(line, visibleStart, visibleCount, xForIndex, yForPrice, pulse, size) {
  const start = line.startIndex - visibleStart;
  const end = line.endIndex - visibleStart;
  if (end < 0 || start > visibleCount - 1) return;

  const clippedStart = clamp(start, 0, visibleCount - 1);
  const clippedEnd = clamp(end, 0, visibleCount - 1);
  const xStart = xForIndex(clippedStart);
  const xEnd = xForIndex(clippedEnd);
  const y = yForPrice(line.level);

  ctx.save();
  ctx.strokeStyle = line.color;
  ctx.globalAlpha = line.completed ? 0.72 : 0.95;
  ctx.lineWidth = line.completed ? 2 : 2.4;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.moveTo(xStart, y);
  ctx.lineTo(xEnd, y);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();

  if (start >= 0 && start <= visibleCount - 1) {
    const xA = xForIndex(start);
    drawPoint(xA, y, line.color, true, pulse * 0.32);
    ctx.fillStyle = "#f2f5f6";
    ctx.font = "900 11px Consolas, monospace";
    ctx.fillText("A", xA - 4, y - 22);
  }

  if (line.completed && end >= 0 && end <= visibleCount - 1) {
    const xB = xForIndex(end);
    drawPoint(xB, y, line.color, false, pulse * 0.24);
    ctx.fillStyle = "#f2f5f6";
    ctx.font = "900 11px Consolas, monospace";
    ctx.fillText("B", xB - 4, y - 22);
  }

  const shouldBadge = !line.completed || end >= visibleCount - 22 || start >= visibleCount - 60;
  if (shouldBadge) {
    drawBadge(xEnd, y, line.color, `VOLVERA -> ${formatPrice(line.level)}`, size);
  }
}

function drawMarketChart(snapshot, now) {
  const size = resizeNodoCanvas();
  if (!size) return;

  const { width, height } = size;
  const frame = currentTimeframe();
  const chartWorld = buildTimeframeWorld(snapshot.points, frame);
  const margin = { left: 54, right: 58, top: 54, bottom: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const visibleCount = Math.min(132, chartWorld.points.length);
  const visibleStart = chartWorld.points.length - visibleCount;
  const price = chartWorld.points.slice(-visibleCount);
  const ema20Series = chartWorld.ema20.slice(-visibleCount);
  const ema50Series = chartWorld.ema50.slice(-visibleCount);
  const candidateLines = chartWorld.queroLines.length ? chartWorld.queroLines.slice(-9) : [chartWorld.nodeOne, chartWorld.nodeTwo];
  const drawableLines = candidateLines.filter((line) => line.endIndex >= visibleStart && line.startIndex <= chartWorld.points.length - 1);
  const lineLevels = drawableLines.map((line) => line.level);
  const all = [...price, ...ema20Series, ...ema50Series, ...lineLevels];
  const min = Math.min(...all) - 1.2;
  const max = Math.max(...all) + 1.2;
  const range = max - min || 1;
  const pulse = (Math.sin(now / 240) + 1) * 2.2;

  const xForIndex = (index) => margin.left + (index / Math.max(1, visibleCount - 1)) * plotWidth;
  const yForPrice = (value) => margin.top + (1 - (value - min) / range) * plotHeight;
  const mapper = (value, index) => [xForIndex(index), yForPrice(value)];

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "rgba(95, 111, 130, .22)";
  ctx.lineWidth = 1;
  for (let x = margin.left; x <= width - margin.right; x += plotWidth / 8) {
    ctx.beginPath();
    ctx.moveTo(x, margin.top);
    ctx.lineTo(x, height - margin.bottom);
    ctx.stroke();
  }
  for (let i = 0; i <= 4; i += 1) {
    const offset = Math.round(((visibleCount - 1) / 4) * i);
    const x = xForIndex(offset);
    const minutesBack = Math.max(0, (visibleCount - 1 - offset) * frame.minutes);
    ctx.fillStyle = "#677588";
    ctx.font = "700 11px Consolas, monospace";
    ctx.textAlign = i === 0 ? "left" : i === 4 ? "right" : "center";
    ctx.fillText(formatMinutesBack(minutesBack), x, height - margin.bottom + 18);
  }
  ctx.textAlign = "left";
  for (let i = 0; i <= 5; i += 1) {
    const y = margin.top + (plotHeight / 5) * i;
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(width - margin.right, y);
    ctx.stroke();
    const label = max - (range / 5) * i;
    ctx.fillStyle = "#677588";
    ctx.font = "700 12px Consolas, monospace";
    ctx.fillText(label.toFixed(1), width - margin.right + 12, y + 4);
  }

  drawLine(ema50Series, "#9d7cff", 2.2, mapper);
  drawLine(ema20Series, "#1aa4ff", 2.6, mapper);
  drawLine(price, "#f2f5f6", 2.3, mapper);

  drawableLines.forEach((line) => {
    drawQueroLine(line, visibleStart, visibleCount, xForIndex, yForPrice, pulse * 0.45, size);
  });

  const lastX = xForIndex(visibleCount - 1);
  const lastY = yForPrice(price.at(-1));
  ctx.fillStyle = "#101827";
  ctx.beginPath();
  ctx.arc(lastX, lastY, 4 + pulse * 0.4, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = snapshot.regime === "alcista" ? "#00d57e" : snapshot.regime === "bajista" ? "#ff4048" : "#ffa027";
  ctx.font = "900 13px Consolas, monospace";
  ctx.fillText(`${market.source}  ${frame.label}  ${snapshot.regime.toUpperCase()}  ${formatPrice(snapshot.last)}`, margin.left, height - 6);
}

function renderDashboard(snapshot) {
  renderSensors(snapshot);
  renderThermo(snapshot);
  renderNodes(snapshot);
  renderSequence(snapshot);
  updateSystemStrip(snapshot);
}

function animateNodo(now = 0) {
  if (!market.snapshot || (!market.paused && now - market.lastTickAt > 520)) {
    if (market.snapshot) pushSimPoint();
    market.snapshot = buildSnapshot();
    renderDashboard(market.snapshot);
    market.lastTickAt = now;
  }
  if (market.snapshot) drawMarketChart(market.snapshot, now);
  requestAnimationFrame(animateNodo);
}

pauseButton.addEventListener("click", () => {
  market.paused = !market.paused;
  pauseButton.textContent = market.paused ? "Reanudar" : "\u23f8\ufe0f Pausar";
  if (!market.paused) market.lastTickAt = performance.now();
});

sourceButton.addEventListener("click", () => {
  seedMarket();
  market.snapshot = buildSnapshot();
  renderDashboard(market.snapshot);
});

apiButton.addEventListener("click", async () => {
  apiButton.disabled = true;
  apiButton.textContent = "CARGANDO";
  try {
    const response = await fetch("/api/market/btc?symbol=BTC-USD");
    if (!response.ok) throw new Error(`API ${response.status}`);
    const payload = await response.json();
    const closes = payload.points.map((point) => Number(point.close)).filter(Number.isFinite);
    if (closes.length < 40) throw new Error("Serie insuficiente");
    seedMarket(closes);
    market.snapshot = buildSnapshot();
    renderDashboard(market.snapshot);
    apiButton.textContent = "API OK";
  } catch (error) {
    apiButton.textContent = "API FALLA";
    sourceButton.textContent = "SIMULADO";
    market.source = "SIMULADO";
    setTimeout(() => {
      apiButton.textContent = "</> API";
    }, 1800);
  } finally {
    apiButton.disabled = false;
  }
});

timeframeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectTimeframe(button.dataset.timeframe || "1m");
  });
});

window.addEventListener("resize", resizeNodoCanvas);

function money(value) {
  return Number.isFinite(value) ? `$${value.toFixed(2)}` : "invalido";
}

$("#risk-calc").addEventListener("click", () => {
  const capital = Number($("#capital").value);
  const riskPct = Number($("#risk-percent").value);
  const entry = Number($("#entry").value);
  const stop = Number($("#stop").value);
  const target = Number($("#target").value);
  const riskAmount = capital * (riskPct / 100);
  const perUnitRisk = Math.abs(entry - stop);
  const size = perUnitRisk > 0 ? riskAmount / perUnitRisk : NaN;
  const reward = Math.abs(target - entry);
  const rMultiple = perUnitRisk > 0 ? reward / perUnitRisk : NaN;
  const profit = Number.isFinite(size) ? reward * size : NaN;

  $("#risk-output").innerHTML = `
    Riesgo maximo: <strong>${money(riskAmount)}</strong><br>
    Tamano estimado: <strong>${Number.isFinite(size) ? size.toFixed(4) : "invalido"}</strong><br>
    R esperado: <strong>${Number.isFinite(rMultiple) ? rMultiple.toFixed(2) : "invalido"}R</strong><br>
    Ganancia objetivo: <strong>${money(profit)}</strong>
  `;
});

$("#pct-calc").addEventListener("click", () => {
  const a = Number($("#pct-a").value);
  const b = Number($("#pct-b").value);
  const pct = a !== 0 ? ((b - a) / Math.abs(a)) * 100 : NaN;
  $("#pct-output").innerHTML = `
    Cambio: <strong>${Number.isFinite(pct) ? pct.toFixed(2) : "invalido"}%</strong><br>
    Diferencia absoluta: <strong>${Number.isFinite(b - a) ? (b - a).toFixed(2) : "invalido"}</strong>
  `;
});

function renderTrial() {
  const card = trialDeck[trialIndex % trialDeck.length];
  $("#trial-card").textContent = card.text;
  $("#trial-score").textContent = `${trialCorrect} / ${trialTotal}`;
  Object.entries(stats).forEach(([key, value]) => {
    $(`#stat-${key}`).textContent = value;
  });
}

document.querySelectorAll(".choice-grid button").forEach((button) => {
  button.addEventListener("click", () => {
    const card = trialDeck[trialIndex % trialDeck.length];
    const choice = button.dataset.choice;
    trialTotal += 1;
    if (choice === card.answer) {
      trialCorrect += 1;
      stats[card.stat] += 1;
      $("#trial-output").innerHTML = `<strong>Correcto.</strong><br>${card.why}`;
    } else {
      stats.ruido += 1;
      $("#trial-output").innerHTML = `<strong>Custodia corrige.</strong><br>Mejor respuesta: ${card.answer}. ${card.why}`;
    }
    trialIndex += 1;
    renderTrial();
  });
});

seedMarket();
market.snapshot = buildSnapshot();
renderDashboard(market.snapshot);
renderTrial();
setView(document.querySelector(".lab-tab.active")?.dataset.view || "nodo");
requestAnimationFrame(animateNodo);
