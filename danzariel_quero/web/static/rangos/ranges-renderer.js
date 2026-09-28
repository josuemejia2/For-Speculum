(function () {
  const rootSelector = "#ranges-quero-root";
  const engine = window.QueroRangesEngine;
  const store = window.QueroRangesState;

  function fmt(value, digits = 2) {
    if (value === null || value === undefined || value === "") return "--";
    const number = Number(value);
    return Number.isFinite(number) ? number.toFixed(digits) : "--";
  }

  function input(field, value, type = "number") {
    const inputMode = type === "number" ? ' inputmode="decimal"' : "";
    return `<input class="rq-input" data-rq-field="${field}" type="text" value="${value}"${inputMode} autocomplete="off" spellcheck="false" />`;
  }

  function select(field, value) {
    return `
      <select class="rq-input" data-rq-field="${field}">
        <option value="SI" ${value === "SI" ? "selected" : ""}>SI</option>
        <option value="NO" ${value === "NO" ? "selected" : ""}>NO</option>
      </select>
    `;
  }

  function arrow(result, compact = false) {
    const symbol = result.direction === "up" ? "&#8593;" : result.direction === "down" ? "&#8595;" : "&#8212;";
    const label = result.direction === "up" ? "VERDE" : result.direction === "down" ? "ROJO" : "AMARILLO";
    return `<div class="rq-arrow ${result.direction}${compact ? " compact" : ""}"><b>${symbol}</b><span>${label}</span></div>`;
  }

  function auto(value) {
    return `<span class="rq-auto">${fmt(value)}</span>`;
  }

  function readValue(value) {
    return `<span class="rq-readonly">${fmt(value)}</span>`;
  }

  function unknown(result) {
    return result?.value === null || result?.value === undefined ? "--" : fmt(result.value);
  }

  function swingValue(result) {
    if (!result || result.upper === null || result.lower === null) return "--";
    return `<span>&#9650; ${fmt(result.upper)}<br>&#9660; ${fmt(result.lower)}</span>`;
  }

  function directionTitle(result) {
    if (!result) return "";
    const upper = result.distanceHigh ?? result.distanceToOverbought;
    const lower = result.distanceLow ?? result.distanceToOversold;
    const direction = result.direction || "neutral";
    return ` title="direccion: ${direction}; distancia superior: ${fmt(upper)}; distancia inferior: ${fmt(lower)}"`;
  }

  function blockRows(rows) {
    return rows.map((row) => `
      <div class="rq-row">
        <span>${row[0]}</span>
        <b>${row[1]}</b>
      </div>
    `).join("");
  }

  function topBlockShell(blockNumber, title, rows, result) {
    return `
      <section class="rq-card" data-rq-direction="${result?.direction || "neutral"}"${directionTitle(result)}>
        <header>
          <strong>BLOQUE ${blockNumber}</strong>
          <h3>${title}</h3>
        </header>
        <div class="rq-range-box-body">
          <div class="rq-card-rows">${blockRows(rows)}</div>
          ${arrow(result, true)}
        </div>
      </section>
    `;
  }

  function rangeBlock({ title, highLabel, lowLabel, highField, lowField, range, price, blockNumber, result, editable = true }) {
    return topBlockShell(blockNumber, title, [
      [highLabel, editable ? input(highField, range.high) : readValue(range.high)],
      ["Distancia", auto(result?.distanceHigh)],
      ["Precio", `<span class="rq-shared-price">${fmt(price)}</span>`],
      ["Distancia", auto(result?.distanceLow)],
      [lowLabel, editable ? input(lowField, range.low) : readValue(range.low)],
    ], result);
  }

  function overboughtOversoldBlock(state, overboughtLevel, oversoldLevel, result) {
    return topBlockShell(1, "Rangos del Día", [
      ["Sobrecompra", auto(overboughtLevel)],
      ["Distancia SC", auto(result?.distanceToOverbought)],
      ["Precio", `<span class="rq-shared-price">${fmt(state.price)}</span>`],
      ["Distancia SV", auto(result?.distanceToOversold)],
      ["Sobreventa", auto(oversoldLevel)],
    ], result);
  }

  function engineTable(state) {
    const rows = [
      ["1 Dia", "emaSvDay", "oversoldDay", "overboughtDay", "emaScDay", state.emaOversold.day, state.oversoldLevels.day, state.overboughtLevels.day, state.emaOverbought.day],
      ["1 Hora", "emaSvHour", "oversoldHour", "overboughtHour", "emaScHour", state.emaOversold.hour, state.oversoldLevels.hour, state.overboughtLevels.hour, state.emaOverbought.hour],
      ["30 Min", "emaSv30m", "oversold30m", "overbought30m", "emaSc30m", state.emaOversold.min30, state.oversoldLevels.min30, state.overboughtLevels.min30, state.emaOverbought.min30],
      ["15 Min", "emaSv15m", "oversold15m", "overbought15m", "emaSc15m", state.emaOversold.min15, state.oversoldLevels.min15, state.overboughtLevels.min15, state.emaOverbought.min15],
    ];

    return `
      <section class="rq-table-card">
        <h3>Motor de Sobrecompra / Sobreventa</h3>
        <table class="rq-table">
          <thead>
            <tr>
              <th rowspan="2">Timeframe</th>
              <th colspan="2">Sobreventa</th>
              <th colspan="2">Sobrecompra</th>
            </tr>
            <tr>
              <th>EMA (SV)</th>
              <th>Nivel SV</th>
              <th>Nivel SC</th>
              <th>EMA (SC)</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <th>${row[0]}</th>
                <td>${input(row[1], row[5], "text")}</td>
                <td>${input(row[2], row[6])}</td>
                <td>${input(row[3], row[7])}</td>
                <td>${input(row[4], row[8], "text")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </section>
    `;
  }

  function auxiliaryModules(state, auxiliaryRanges) {
    const rotation = engine.calculateRotation920Signal(state.rotation920);
    const swingIntermedio = {
      upper: auxiliaryRanges.swingIntermediateUpper,
      lower: auxiliaryRanges.swingIntermediateLower,
    };
    const swingMaximo = {
      upper: auxiliaryRanges.swingMaximumUpper,
      lower: auxiliaryRanges.swingMaximumLower,
    };
    return `
      <section class="rq-aux-card">
        <h3>Modulo Auxiliar</h3>
        <div class="rq-aux-top">
          <div class="rq-aux-cell">
            <h4>Swing Intermedio</h4>
            <strong>${swingValue(swingIntermedio)}</strong>
          </div>
          <div class="rq-aux-cell">
            <h4>Swing Maximo</h4>
            <strong>${swingValue(swingMaximo)}</strong>
          </div>
          <div class="rq-aux-cell rq-rotation ${rotation.direction}">
            <h4>Rotacion Vela 15 Min</h4>
            <p>Rotacion positiva 9/20</p>
            <div class="rq-rotation-line">
              ${select("rotation920", state.rotation920)}
              ${arrow(rotation, true)}
            </div>
          </div>
        </div>
        <div class="rq-open-line">
          <span>Apertura</span>
          ${select("apertura", state.apertura)}
        </div>
        <div class="rq-day-lines">
          ${blockRows([
            ["Maximo Dia", input("dayHigh", state.dayRange.high)],
            ["Minimo Dia", input("dayLow", state.dayRange.low)],
            ["Diferencia", fmt(auxiliaryRanges.difference)],
            ["Intermedio", fmt(auxiliaryRanges.intermediate)],
            ["Maximo", unknown({ value: auxiliaryRanges.auxiliaryMaximum })],
          ])}
        </div>
      </section>
    `;
  }

  function render() {
    const root = document.querySelector(rootSelector);
    if (!root || !engine || !store) return;
    const state = store.clone();
    const oversoldLevel = engine.calculateOversoldLevel(Object.values(state.oversoldLevels));
    const overboughtLevel = engine.calculateOverboughtLevel(Object.values(state.overboughtLevels));
    const panelResults = engine.calculatePanelResults({ state, overboughtLevel, oversoldLevel });
    const auxiliaryRanges = engine.calculateAuxiliaryRanges({
      dayHigh: state.dayRange.high,
      dayLow: state.dayRange.low,
      averageOversold: oversoldLevel,
      averageOverbought: overboughtLevel,
      apertura: state.apertura,
    });

    root.innerHTML = `
      <section class="rq-shell">
        <header class="rq-title-header">
          <div class="rq-title-box">
            <p class="rq-kicker">INDICADOR</p>
            <h2>INDICADOR DE RANGOS QUERO</h2>
          </div>
          <div class="rq-market-line">
            <span>Activo</span>
            ${input("symbol", state.symbol, "text")}
            ${input("pair", state.pair, "text")}
          </div>
        </header>
        <div class="rq-panel-grid">
          ${overboughtOversoldBlock(state, overboughtLevel, oversoldLevel, panelResults.overboughtOversold)}
          ${rangeBlock({ title: "Máx/Min del Día", highLabel: "Máximo Día", lowLabel: "Mínimo Día", highField: "dayHigh", lowField: "dayLow", range: state.dayRange, price: state.price, blockNumber: 2, result: panelResults.day, editable: false })}
          ${rangeBlock({ title: "Rangos del Mes", highLabel: "Máximo Mes", lowLabel: "Mínimo Mes", highField: "monthHigh", lowField: "monthLow", range: state.monthRange, price: state.price, blockNumber: 3, result: panelResults.month })}
          ${rangeBlock({ title: "Rangos del Año", highLabel: "Máximo Año", lowLabel: "Mínimo Año", highField: "yearHigh", lowField: "yearLow", range: state.yearRange, price: state.price, blockNumber: 4, result: panelResults.year })}
        </div>
        <div class="rq-main-grid">
          ${engineTable(state)}
          ${auxiliaryModules(state, auxiliaryRanges)}
        </div>
        <section class="rq-bottom-strip">
          <div>Precio <b>${input("price", state.price)}</b></div>
          <div>Promedios <b>${fmt(oversoldLevel)} / ${fmt(overboughtLevel)}</b></div>
          <div>Ruptura-Apertura <b>${unknown({ value: auxiliaryRanges.ruptureOpening })}</b></div>
          <div>Promedio Diario <b>${fmt(state.dailyAverage)}</b></div>
        </section>
        <footer class="rq-footer">
          <div>Recuerde completar la anticipacion</div>
          <div>${new Date().toLocaleDateString("en-US", { month: "long", day: "2-digit" })} - ${new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}</div>
          <div>Version 23 de Mayo del 2024&copy;</div>
        </footer>
      </section>
    `;
  }

  function updateFromField(target, options = {}) {
    const { renderNow = true, restoreFocus = true } = options;
    const field = target?.dataset?.rqField;
    if (!field) return;
    const selectionStart = typeof target.selectionStart === "number" ? target.selectionStart : null;
    store.setField(field, target.value);
    if (!renderNow) return;
    render();
    if (!restoreFocus) return;
    const next = document.querySelector(`[data-rq-field="${field}"]`);
    if (!next) return;
    next.focus();
    if (selectionStart !== null && typeof next.setSelectionRange === "function") {
      const cursor = Math.min(selectionStart, next.value.length);
      next.setSelectionRange(cursor, cursor);
    }
  }

  function bind() {
    const root = document.querySelector(rootSelector);
    if (!root) return;
    root.addEventListener("input", (event) => {
      if (!event.target?.matches?.(".rq-input")) return;
      if (event.target.tagName === "SELECT") return;
      updateFromField(event.target, { renderNow: false });
    });
    root.addEventListener("change", (event) => {
      if (!event.target?.matches?.(".rq-input")) return;
      updateFromField(event.target, { renderNow: true, restoreFocus: event.target.tagName === "SELECT" });
    });
    root.addEventListener("focusout", (event) => {
      if (!event.target?.matches?.("input.rq-input")) return;
      updateFromField(event.target, { renderNow: true, restoreFocus: false });
    });
    root.addEventListener("keydown", (event) => {
      if (!event.target?.matches?.("input.rq-input")) return;
      if (event.key !== "Enter") return;
      event.preventDefault();
      updateFromField(event.target, { renderNow: true, restoreFocus: true });
    });
  }

  function init() {
    bind();
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
