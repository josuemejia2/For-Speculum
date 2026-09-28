(function () {
  function numberOrNull(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function average(values) {
    const clean = values.map(numberOrNull).filter((value) => value !== null);
    if (!clean.length) return null;
    return clean.reduce((sum, value) => sum + value, 0) / clean.length;
  }

  function compareDistances(upperDistance, lowerDistance) {
    if (upperDistance === null || lowerDistance === null) return { direction: "neutral", state: "no-data" };
    const tolerance = 0.000001;
    if (Math.abs(upperDistance - lowerDistance) <= tolerance) return { direction: "neutral", state: "center" };
    if (upperDistance < lowerDistance) return { direction: "up", state: "closer-to-high" };
    return { direction: "down", state: "closer-to-low" };
  }

  function calculateRangePosition({ high, low, price }) {
    const highValue = numberOrNull(high);
    const lowValue = numberOrNull(low);
    const priceValue = numberOrNull(price);
    if (highValue === null || lowValue === null || priceValue === null) {
      return {
        high: highValue,
        low: lowValue,
        price: priceValue,
        distanceHigh: null,
        distanceLow: null,
        midpoint: null,
        direction: "neutral",
        state: "no-data",
      };
    }

    const distanceHigh = Math.abs(highValue - priceValue);
    const distanceLow = Math.abs(priceValue - lowValue);
    const position = compareDistances(distanceHigh, distanceLow);
    return {
      high: highValue,
      low: lowValue,
      price: priceValue,
      distanceHigh,
      distanceLow,
      midpoint: (highValue + lowValue) / 2,
      ...position,
    };
  }

  function calculateOversoldLevel(values) {
    return average(values);
  }

  function calculateOverboughtLevel(values) {
    return average(values);
  }

  function calculateOverboughtOversoldPosition({ overboughtLevel, oversoldLevel, price }) {
    const overbought = numberOrNull(overboughtLevel);
    const oversold = numberOrNull(oversoldLevel);
    const priceValue = numberOrNull(price);
    if (overbought === null || oversold === null || priceValue === null) {
      return {
        overboughtLevel: overbought,
        oversoldLevel: oversold,
        price: priceValue,
        distanceToOverbought: null,
        distanceToOversold: null,
        direction: "neutral",
        state: "no-data",
      };
    }

    const distanceToOverbought = Math.abs(overbought - priceValue);
    const distanceToOversold = Math.abs(priceValue - oversold);
    const position = compareDistances(distanceToOverbought, distanceToOversold);
    return {
      overboughtLevel: overbought,
      oversoldLevel: oversold,
      price: priceValue,
      distanceToOverbought,
      distanceToOversold,
      direction: position.direction,
      state: position.direction === "up" ? "closer-to-overbought" : position.direction === "down" ? "closer-to-oversold" : position.state,
    };
  }

  function calculateRotation920Signal(value) {
    const normalized = String(value || "").trim().toLowerCase();
    if (["si", "sí", "s", "yes", "true"].includes(normalized)) {
      return { value: "SI", direction: "up", state: "positive" };
    }
    if (["no", "n", "false"].includes(normalized)) {
      return { value: "NO", direction: "down", state: "negative" };
    }
    return { value: "--", direction: "neutral", state: "neutral" };
  }

  function calculateDayMetrics({ high, low }) {
    const highValue = numberOrNull(high);
    const lowValue = numberOrNull(low);
    if (highValue === null || lowValue === null) {
      return { difference: null, midpoint: null, maximum: null };
    }
    return {
      difference: highValue - lowValue,
      midpoint: (highValue + lowValue) / 2,
      maximum: null,
    };
  }

  function calculateAuxiliaryRanges({ dayHigh, dayLow, averageOversold, averageOverbought, apertura }) {
    const highValue = numberOrNull(dayHigh);
    const lowValue = numberOrNull(dayLow);
    const oversoldValue = numberOrNull(averageOversold);
    const overboughtValue = numberOrNull(averageOverbought);
    const difference = highValue === null || lowValue === null ? null : highValue - lowValue;
    const ruptureOpening = oversoldValue === null || overboughtValue === null ? null : (oversoldValue + overboughtValue) / 2;
    const normalizedApertura = String(apertura || "").trim().toUpperCase();

    if (normalizedApertura !== "NO" || difference === null) {
      return {
        difference,
        intermediate: null,
        auxiliaryMaximum: null,
        ruptureOpening,
        swingIntermediateUpper: null,
        swingIntermediateLower: null,
        swingMaximumUpper: null,
        swingMaximumLower: null,
        state: normalizedApertura === "SI" ? "apertura-si-pending" : "unknown",
      };
    }

    const intermediate = difference * 0.165;
    const auxiliaryMaximum = difference * 0.33;
    return {
      difference,
      intermediate,
      auxiliaryMaximum,
      ruptureOpening,
      swingIntermediateUpper: ruptureOpening === null ? null : ruptureOpening + intermediate,
      swingIntermediateLower: ruptureOpening === null ? null : ruptureOpening - intermediate,
      swingMaximumUpper: ruptureOpening === null ? null : ruptureOpening + auxiliaryMaximum,
      swingMaximumLower: ruptureOpening === null ? null : ruptureOpening - auxiliaryMaximum,
      state: "apertura-no-confirmed",
    };
  }

  function calculateSwingIntermediate(context) {
    const ranges = calculateAuxiliaryRanges(context || {});
    return {
      upper: ranges.swingIntermediateUpper,
      lower: ranges.swingIntermediateLower,
      state: ranges.state,
    };
  }

  function calculateSwingMaximum(context) {
    const ranges = calculateAuxiliaryRanges(context || {});
    return {
      upper: ranges.swingMaximumUpper,
      lower: ranges.swingMaximumLower,
      state: ranges.state,
    };
  }

  function calculateAuxiliaryMaximum(context) {
    return calculateAuxiliaryRanges(context || {}).auxiliaryMaximum;
  }

  function calculateSwingIntermedio(context) {
    return calculateSwingIntermediate(context);
  }

  function calculateSwingMaximo(context) {
    return calculateSwingMaximum(context);
  }

  function calculateRuptureApertura(context) {
    return { value: calculateAuxiliaryRanges(context || {}).ruptureOpening, state: "calculated" };
  }

  function calculatePanelResults({ state, overboughtLevel, oversoldLevel }) {
    return {
      overboughtOversold: calculateOverboughtOversoldPosition({
        overboughtLevel,
        oversoldLevel,
        price: state.price,
      }),
      day: calculateRangePosition({
        high: state.dayRange?.high,
        low: state.dayRange?.low,
        price: state.price,
      }),
      month: calculateRangePosition({
        high: state.monthRange?.high,
        low: state.monthRange?.low,
        price: state.price,
      }),
      year: calculateRangePosition({
        high: state.yearRange?.high,
        low: state.yearRange?.low,
        price: state.price,
      }),
    };
  }

  window.QueroRangesEngine = {
    calculateRangePosition,
    calculateOversoldLevel,
    calculateOverboughtLevel,
    calculateOverboughtOversoldPosition,
    calculateRotation920Signal,
    calculateDayMetrics,
    calculateAuxiliaryRanges,
    calculateSwingIntermediate,
    calculateSwingMaximum,
    calculateAuxiliaryMaximum,
    calculateSwingIntermedio,
    calculateSwingMaximo,
    calculateRuptureApertura,
    calculatePanelResults,
  };
})();
