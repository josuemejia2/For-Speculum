export function createCategoryButton(category, isActive) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `category-item${isActive ? " active" : ""}`;
  button.setAttribute("aria-current", isActive ? "page" : "false");
  button.innerHTML = `
    <span class="category-orb">${category.icon}</span>
    <span class="category-label">${category.label}</span>
  `;
  return button;
}

export function createSubmenuItem(item, isActive) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `menu-card${isActive ? " active" : ""}`;
  button.innerHTML = `
    <span class="menu-index">${item.code}</span>
    <span>
      <strong>${item.title}</strong>
      <small>${item.subtitle}</small>
    </span>
  `;
  return button;
}

function metricMarkup(metrics = []) {
  return metrics
    .map((metric) => `
      <div class="metric">
        <span>${metric.label}</span>
        <strong>${metric.value}</strong>
      </div>
    `)
    .join("");
}

function cardMarkup(cards = []) {
  return cards
    .map((card) => `
      <article class="module-card">
        <span class="card-kicker">${card.kicker}</span>
        <h3>${card.header}</h3>
        <p>${card.description}</p>
        <small>${card.footnote}</small>
      </article>
    `)
    .join("");
}

export function createModuleView(payload, isOpen) {
  const wrapper = document.createElement("div");
  wrapper.className = `module-shell${isOpen ? " expanded" : ""}`;
  wrapper.innerHTML = `
    <div class="module-headline">
      <div>
        <p class="panel-kicker">${payload.kicker}</p>
        <h2>${payload.title}</h2>
        <p class="module-meta">${payload.subtitle}</p>
      </div>
      <span class="status-pill">${payload.status}</span>
    </div>

    <div class="module-body">
      <section class="primary-module">
        <div class="module-visual" aria-hidden="true">
          <span></span><span></span><span></span>
        </div>
        <div class="primary-copy">
          <h3>${payload.focus}</h3>
          <p>${payload.description}</p>
        </div>
      </section>

      <section class="metric-grid">
        ${metricMarkup(payload.metrics)}
      </section>

      <section class="module-cards">
        ${cardMarkup(payload.cards)}
      </section>
    </div>
  `;
  return wrapper;
}
