(function () {
  const GAP_TOLERANCE = 0.0015;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function finite(value) {
    return Number.isFinite(Number(value));
  }

  function fmt(value, digits = 2) {
    if (!finite(value)) return "--";
    return Number(value).toFixed(digits);
  }

  function signed(value, digits = 2) {
    if (!finite(value)) return "--";
    const number = Number(value);
    return `${number >= 0 ? "+" : ""}${number.toFixed(digits)}`;
  }

  function mark(pass) {
    return pass ? "OK" : "--";
  }

  function classForState(state) {
    if (state === "bullish") return "good";
    if (state === "bearish") return "danger";
    return state;
  }

  function makeSensor(data) {
    const state = data.state || "neutral";
    return {
      directional: true,
      score: 0,
      state,
      className: classForState(state) || "neutral",
      ...data,
      state,
      className: data.className || classForState(state) || "neutral",
    };
  }

  function gapSensor({ index, name, role, fast, slow, previousFast, previousSlow, fastLabel, slowLabel }) {
    if (![fast, slow, previousFast, previousSlow].every(finite)) {
      return makeSensor({
        index,
        name,
        role,
        stateLabel: "SIN DATA",
        detail: `${fastLabel}/${slowLabel}`,
        value: "esperando velas",
      });
    }

    const gap = fast - slow;
    const previousGap = previousFast - previousSlow;
    const reference = Math.max(Math.abs(slow), Math.abs(fast), 1);
    const normalized = gap / reference;
    const converging = Math.abs(gap) < Math.abs(previousGap) * 0.86;
    const widening = Math.abs(gap) > Math.abs(previousGap) * 1.08;
    const strength = clamp(Math.abs(normalized) / 0.018, 0.2, 1);
    const detail = `${fastLabel} ${gap >= 0 ? ">" : "<"} ${slowLabel}`;
    const value = `${signed(normalized * 100, 2)}%`;

    if (Math.abs(normalized) <= GAP_TOLERANCE) {
      return makeSensor({
        index,
        name,
        role,
        state: "neutral",
        stateLabel: "NEUTRAL",
        detail: `${fastLabel}/${slowLabel} en tolerancia`,
        value,
      });
    }

    if (gap > 0) {
      return makeSensor({
        index,
        name,
        role,
        state: converging && !widening ? "transition-bearish" : "bullish",
        stateLabel: converging && !widening ? "ALCISTA CEDIENDO" : "ALCISTA",
        detail,
        value,
        score: converging && !widening ? 0.3 : strength,
      });
    }

    return makeSensor({
      index,
      name,
      role,
      state: converging && !widening ? "transition-bullish" : "bearish",
      stateLabel: converging && !widening ? "BAJISTA CEDIENDO" : "BAJISTA",
      detail,
      value,
      score: converging && !widening ? -0.3 : -strength,
    });
  }

  function entryCandleSensor(data) {
    const current = [data.open, data.low, data.high, data.close, data.ema3];
    const previous = [data.previousOpen, data.previousLow, data.previousHigh];
    if (![...current, ...previous].every(finite)) {
      return makeSensor({
        index: 1,
        name: "VELA DE ENTRADA",
        role: "VALIDACION",
        stateLabel: "SIN DATA",
        detail: "faltan velas comparables",
        value: "0/3",
      });
    }

    const longOpenOk = data.open > data.previousOpen;
    const longLowOk = data.low > data.previousLow;
    const longHighOk = data.high > data.previousHigh;
    const shortOpenOk = data.open < data.previousOpen;
    const shortLowOk = data.low < data.previousLow;
    const shortHighOk = data.high < data.previousHigh;
    const longPoints = [longOpenOk, longLowOk, longHighOk].filter(Boolean).length;
    const shortPoints = [shortOpenOk, shortLowOk, shortHighOk].filter(Boolean).length;
    const wantsShort = shortPoints > longPoints;
    const points = wantsShort ? shortPoints : longPoints;
    const checks = wantsShort
      ? `O ${mark(shortOpenOk)} / L ${mark(shortLowOk)} / H ${mark(shortHighOk)}`
      : `O ${mark(longOpenOk)} / L ${mark(longLowOk)} / H ${mark(longHighOk)}`;
    const emaOk = wantsShort ? data.close < data.ema3 : data.close > data.ema3;
    const side = wantsShort ? "CORTO" : "LARGO";
    const hasCloseFlag = typeof data.isCandleClosed === "boolean";

    if (points === 3 && hasCloseFlag && data.isCandleClosed && emaOk) {
      return makeSensor({
        index: 1,
        name: wantsShort ? "VELA DE SALIDA" : "VELA DE ENTRADA",
        role: "VALIDACION",
        state: wantsShort ? "bearish" : "bullish",
        stateLabel: wantsShort ? "CORTO VALIDADO" : "LARGO VALIDADO",
        detail: `${side} 3/3`,
        value: wantsShort ? "C < EMA3 OK" : "C > EMA3 OK",
        score: wantsShort ? -1 : 1,
      });
    }

    if (points === 3 && hasCloseFlag && data.isCandleClosed && !emaOk) {
      return makeSensor({
        index: 1,
        name: wantsShort ? "VELA DE SALIDA" : "VELA DE ENTRADA",
        role: "VALIDACION",
        state: wantsShort ? "transition-bullish" : "transition-bearish",
        stateLabel: "NO VALIDADA",
        detail: `${side} 3/3`,
        value: wantsShort ? "C >= EMA3" : "C <= EMA3",
        score: 0,
      });
    }

    if (points === 3) {
      return makeSensor({
        index: 1,
        name: wantsShort ? "VELA DE SALIDA" : "VELA DE ENTRADA",
        role: "VALIDACION",
        state: wantsShort ? "transition-bearish" : "transition-bullish",
        stateLabel: wantsShort ? "CORTO CANDIDATO" : "LARGO CANDIDATO",
        detail: `${side} 3/3`,
        value: emaOk && !hasCloseFlag ? (wantsShort ? "C < EMA3 ?" : "C > EMA3 ?") : checks,
        score: wantsShort ? (emaOk ? -0.65 : -0.45) : emaOk ? 0.65 : 0.45,
      });
    }

    if (points > 0) {
      return makeSensor({
        index: 1,
        name: wantsShort ? "VELA DE SALIDA" : "VELA DE ENTRADA",
        role: "VALIDACION",
        state: "neutral",
        stateLabel: "DESARROLLO",
        detail: `${side} ${points}/3`,
        value: checks,
        score: points === 2 ? (wantsShort ? -0.18 : 0.18) : 0,
      });
    }

    return makeSensor({
      index: 1,
      name: "VELA DE ENTRADA",
      role: "VALIDACION",
      state: "neutral",
      stateLabel: "SIN ESTRUCTURA",
      detail: "0/3",
      value: checks,
    });
  }

  function macdSensor(data) {
    if (![data.macdHistogram, data.previousMacdHistogram].every(finite)) {
      return makeSensor({
        index: 6,
        name: "MACD",
        role: "MOMENTUM",
        stateLabel: "SIN DATA",
        detail: "histograma pendiente",
        value: "--",
      });
    }

    const hist = data.macdHistogram;
    const rising = hist > data.previousMacdHistogram;
    const abs = Math.max(Math.abs(hist), 0.01);
    if (hist >= 0) {
      return makeSensor({
        index: 6,
        name: "MACD",
        role: "MOMENTUM",
        state: rising ? "bullish" : "transition-bearish",
        stateLabel: rising ? "IMPULSO +" : "PIERDE FUERZA",
        detail: `HIST ${signed(hist, 2)} ${rising ? "SUBE" : "BAJA"}`,
        value: rising ? "MOMENTUM +" : "ALERTA",
        score: rising ? clamp(abs / 0.75, 0.35, 1) : 0.25,
      });
    }

    return makeSensor({
      index: 6,
      name: "MACD",
      role: "MOMENTUM",
      state: rising ? "transition-bullish" : "bearish",
      stateLabel: rising ? "RECUPERA" : "IMPULSO -",
      detail: `HIST ${signed(hist, 2)} ${rising ? "SUBE" : "BAJA"}`,
      value: rising ? "RECUPERA" : "MOMENTUM -",
      score: rising ? -0.25 : -clamp(abs / 0.75, 0.35, 1),
    });
  }

  function sarSensor(data) {
    if (![data.close, data.previousClose, data.sar, data.previousSar].every(finite)) {
      return makeSensor({
        index: 7,
        name: "SAR",
        role: "DIRECCION",
        stateLabel: "SIN DATA",
        detail: "SAR pendiente",
        value: "--",
      });
    }

    const above = data.close > data.sar;
    const wasAbove = data.previousClose > data.previousSar;
    const rotated = above !== wasAbove;
    return makeSensor({
      index: 7,
      name: "SAR",
      role: "DIRECCION",
      state: above ? (rotated ? "transition-bullish" : "bullish") : rotated ? "transition-bearish" : "bearish",
      stateLabel: above ? (rotated ? "ROTACION +" : "ALCISTA") : rotated ? "ROTACION -" : "BAJISTA",
      detail: above ? "SAR < PRECIO" : "SAR > PRECIO",
      value: rotated ? (above ? "ROTACION +" : "ROTACION -") : signed(data.close - data.sar),
      score: above ? (rotated ? 0.45 : 0.8) : rotated ? -0.45 : -0.8,
    });
  }

  function bollingerSensor(data) {
    const width = finite(data.bollingerBandwidth) ? data.bollingerBandwidth : 0;
    const previousWidth = finite(data.previousBollingerBandwidth) ? data.previousBollingerBandwidth : width;
    let stateLabel = "NORMAL";
    let detail = "precio dentro de bandas";
    let className = "neutral";

    if ([data.close, data.bollingerUpper, data.bollingerLower].every(finite)) {
      if (data.close > data.bollingerUpper) {
        stateLabel = "EXTREMO SUP.";
        detail = "fuera de banda alta";
        className = "mixed";
      } else if (data.close < data.bollingerLower) {
        stateLabel = "EXTREMO INF.";
        detail = "fuera de banda baja";
        className = "mixed";
      } else if (width > previousWidth * 1.08) {
        stateLabel = "EXPANSION";
        detail = "volatilidad abre";
        className = "mixed";
      } else if (width < previousWidth * 0.94) {
        stateLabel = "COMPRESION";
        detail = "volatilidad cierra";
      }
    }

    return makeSensor({
      index: 8,
      name: "BOLLINGER",
      role: "VOLATILIDAD",
      state: className === "mixed" ? "mixed" : "neutral",
      className,
      stateLabel,
      detail: `BW ${fmt(width * 100, 2)}`,
      value: detail,
      directional: false,
      score: 0,
    });
  }

  function calculateSensors(data) {
    return [
      entryCandleSensor(data),
      gapSensor({ index: 2, name: "EMA3 / EMA9", role: "ROTACION", fast: data.ema3, slow: data.ema9, previousFast: data.previousEma3, previousSlow: data.previousEma9, fastLabel: "EMA3", slowLabel: "EMA9" }),
      gapSensor({ index: 3, name: "EMA9/EMA20", role: "TENDENCIA", fast: data.ema9, slow: data.ema20, previousFast: data.previousEma9, previousSlow: data.previousEma20, fastLabel: "EMA9", slowLabel: "EMA20" }),
      gapSensor({ index: 4, name: "EMA20/EMA50", role: "ESTRUCTURA", fast: data.ema20, slow: data.ema50, previousFast: data.previousEma20, previousSlow: data.previousEma50, fastLabel: "EMA20", slowLabel: "EMA50" }),
      gapSensor({ index: 5, name: "EMA50/EMA200", role: "MACRO", fast: data.ema50, slow: data.ema200, previousFast: data.previousEma50, previousSlow: data.previousEma200, fastLabel: "EMA50", slowLabel: "EMA200" }),
      macdSensor(data),
      sarSensor(data),
      bollingerSensor(data),
    ];
  }

  function calculateMarketThermometer(sensors) {
    const directional = sensors.filter((sensor) => sensor.directional !== false && finite(sensor.score));
    const averageScore = directional.length
      ? directional.reduce((sum, sensor) => sum + clamp(sensor.score, -1, 1), 0) / directional.length
      : 0;
    const score = Math.round((clamp(averageScore, -1, 1) + 1) * 50);
    const counts = sensors.reduce(
      (acc, sensor) => {
        if (sensor.state === "bullish") acc.bullish += 1;
        else if (sensor.state === "bearish") acc.bearish += 1;
        else if (sensor.state.startsWith("transition")) acc.transition += 1;
        else acc.neutral += 1;
        return acc;
      },
      { bullish: 0, transition: 0, neutral: 0, bearish: 0 }
    );
    const displayScore = averageScore * 4;
    const regime = displayScore >= 3
      ? "presion alcista fuerte"
      : displayScore >= 1.5
        ? "presion alcista"
        : displayScore >= 0.4
          ? "sesgo alcista"
          : displayScore <= -3
            ? "presion bajista fuerte"
            : displayScore <= -1.5
              ? "presion bajista"
              : displayScore <= -0.4
                ? "sesgo bajista"
                : "equilibrio";
    return {
      score,
      marketScore: averageScore,
      counts,
      good: counts.bullish,
      mixed: counts.transition + counts.neutral,
      regime,
      direction: score >= 63 ? 1 : score <= 37 ? -1 : 0,
    };
  }

  window.QueroSensorEngine = {
    calculateSensors,
    calculateMarketThermometer,
  };
})();
