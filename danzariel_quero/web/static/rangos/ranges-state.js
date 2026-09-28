(function () {
  const state = {
    price: 2.55,
    symbol: "BTC",
    pair: "BTC/USD",
    oversoldLevels: {
      day: 2.0,
      hour: 2.1,
      min30: 2.3,
      min15: 2.4,
    },
    overboughtLevels: {
      day: 3.2,
      hour: 2.8,
      min30: 2.7,
      min15: 2.5,
    },
    emaOversold: {
      day: "9",
      hour: "9",
      min30: "9",
      min15: "20",
    },
    emaOverbought: {
      day: "3",
      hour: "BBT",
      min30: "BBT",
      min15: "BBT",
    },
    dayRange: {
      high: 2.9,
      low: 2.3,
    },
    monthRange: {
      high: 2.0,
      low: 1.0,
    },
    yearRange: {
      high: 3.8,
      low: 1.4,
    },
    rotation920: "SI",
    apertura: "NO",
    dailyAverage: 1500,
  };

  const pathMap = {
    price: ["price"],
    symbol: ["symbol"],
    pair: ["pair"],
    oversoldDay: ["oversoldLevels", "day"],
    oversoldHour: ["oversoldLevels", "hour"],
    oversold30m: ["oversoldLevels", "min30"],
    oversold15m: ["oversoldLevels", "min15"],
    overboughtDay: ["overboughtLevels", "day"],
    overboughtHour: ["overboughtLevels", "hour"],
    overbought30m: ["overboughtLevels", "min30"],
    overbought15m: ["overboughtLevels", "min15"],
    emaSvDay: ["emaOversold", "day"],
    emaSvHour: ["emaOversold", "hour"],
    emaSv30m: ["emaOversold", "min30"],
    emaSv15m: ["emaOversold", "min15"],
    emaScDay: ["emaOverbought", "day"],
    emaScHour: ["emaOverbought", "hour"],
    emaSc30m: ["emaOverbought", "min30"],
    emaSc15m: ["emaOverbought", "min15"],
    dayHigh: ["dayRange", "high"],
    dayLow: ["dayRange", "low"],
    monthHigh: ["monthRange", "high"],
    monthLow: ["monthRange", "low"],
    yearHigh: ["yearRange", "high"],
    yearLow: ["yearRange", "low"],
    rotation920: ["rotation920"],
    apertura: ["apertura"],
    dailyAverage: ["dailyAverage"],
  };

  function clone() {
    return JSON.parse(JSON.stringify(state));
  }

  function setField(field, rawValue) {
    const path = pathMap[field];
    if (!path) return;
    const numeric = !field.startsWith("ema") && !["symbol", "pair", "rotation920", "apertura"].includes(field);
    const normalized = typeof rawValue === "string" ? rawValue.trim().replace(",", ".") : rawValue;
    const value = numeric && normalized !== "" ? Number(normalized) : rawValue;
    let target = state;
    path.slice(0, -1).forEach((key) => {
      target = target[key];
    });
    target[path.at(-1)] = numeric && Number.isFinite(value) ? value : rawValue;
  }

  window.QueroRangesState = {
    clone,
    setField,
  };
})();
