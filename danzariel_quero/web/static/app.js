const areaMeta = {
  inbox: { icon: "📥", label: "Inbox" },
  documentos: { icon: "📄", label: "Documentos" },
  imagenes: { icon: "🖼️", label: "Imagenes" },
  musica: { icon: "🎵", label: "Musica" },
  memoria: { icon: "🧠", label: "Memoria" },
  trading: { icon: "📈", label: "Trading" },
  investigacion: { icon: "🧪", label: "Investigacion" },
  knowledge: { icon: "🔑", label: "Knowledge" },
  bitacora: { icon: "📓", label: "Bitacora" },
};

const areas = Object.keys(areaMeta);

const els = {
  token: document.querySelector("#token"),
  status: document.querySelector("#status"),
  summary: document.querySelector("#summary-card"),
  search: document.querySelector("#global-search"),
  browseArea: document.querySelector("#browse-area"),
  recentList: document.querySelector("#recent-list"),
  browseList: document.querySelector("#browse-list"),
  inboxList: document.querySelector("#inbox-list"),
  searchList: document.querySelector("#search-list"),
  analysis: document.querySelector("#analysis-card"),
  upload: document.querySelector("#upload-file"),
  uploadResult: document.querySelector("#upload-result"),
  noteSheet: document.querySelector("#note-sheet"),
  noteTitle: document.querySelector("#note-title"),
  noteContent: document.querySelector("#note-content"),
  noteResult: document.querySelector("#note-result"),
};

let currentView = "recent";
let selectedInbox = "";
let lastAnalysis = null;
let quickResultTimer = 0;

function token() {
  return localStorage.getItem("dq_token") || "";
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-DQ-Token", token());
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function setStatus(text, online = false) {
  els.status.textContent = text;
  els.status.classList.toggle("online", online);
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(index ? 1 : 0)} ${units[index]}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setView(view) {
  currentView = view;
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((section) => {
    section.classList.toggle("active", section.id === `${view}-view`);
  });
}

function fileUrl(area, path) {
  return `/api/files/download?area=${encodeURIComponent(area)}&path=${encodeURIComponent(path)}`;
}

function areaLabel(area) {
  return areaMeta[area]?.label || area;
}

function areaIcon(area) {
  return areaMeta[area]?.icon || "DQ";
}

function renderList(target, files, options = {}) {
  if (!files.length) {
    target.innerHTML = "<li><div class=\"file-main\"><strong>Sin archivos</strong><span>No hay elementos aqui todavia.</span></div></li>";
    return;
  }

  target.innerHTML = files.map((file) => {
    const filePath = String(file.path || "");
    const selected = options.selectable && selectedInbox === filePath ? " selected" : "";
    const area = String(file.area || options.area || "");
    const safePath = escapeHtml(filePath);
    const safeArea = escapeHtml(area);
    const safeModified = escapeHtml(file.modified || "");
    return `
      <li class="${selected}" data-area="${safeArea}" data-path="${safePath}">
        <span class="area-icon">${escapeHtml(areaIcon(area))}</span>
        <div class="file-main">
          <strong>${safePath}</strong>
          <span>${escapeHtml(areaLabel(area))} · ${formatBytes(file.size)} · ${safeModified}</span>
        </div>
        <div class="file-actions">
          <a href="${fileUrl(area, filePath)}" target="_blank" rel="noreferrer">Abrir</a>
        </div>
      </li>
    `;
  }).join("");

  if (options.selectable) {
    target.querySelectorAll("li").forEach((item) => {
      item.addEventListener("click", () => {
        selectedInbox = item.dataset.path;
        renderList(target, files, options);
      });
    });
  }
}

function renderSummary(data) {
  const area = data.areas || {};
  els.summary.innerHTML = `
    <div class="metric"><b class="metric-icon">🖥️</b><span>Version</span><strong>${data.version || "v0.4"}</strong></div>
    <div class="metric"><b class="metric-icon">💽</b><span>Espacio</span><strong>${formatBytes(data.total_size)}</strong></div>
    <div class="metric"><b class="metric-icon">📄</b><span>Docs</span><strong>${(area.documentos?.count || 0) + (area.memoria?.count || 0)}</strong></div>
    <div class="metric"><b class="metric-icon">🖼️</b><span>Imagenes</span><strong>${area.imagenes?.count || 0}</strong></div>
  `;
  renderList(els.recentList, data.recent || []);
}

function renderAnalysis(data) {
  if (!data) {
    els.analysis.textContent = "Selecciona un archivo de inbox para analizar.";
    return;
  }
  els.analysis.innerHTML = `
    <strong>${escapeHtml(data.archivo)}</strong><br>
    Categoria: ${escapeHtml(data.categoria_sugerida)}<br>
    Destino: ${escapeHtml(data.carpeta_sugerida)}<br>
    Confianza: ${escapeHtml(data.confianza)}%<br>
    ${escapeHtml(data.explicacion)}
  `;
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  renderSummary(data);
}

async function loadBrowse(area = els.browseArea.value) {
  const data = await api(`/api/files?area=${encodeURIComponent(area)}`);
  renderList(els.browseList, data.files || [], { area });
}

async function loadInbox() {
  const data = await api("/api/files?area=inbox");
  renderList(els.inboxList, data.files || [], { area: "inbox", selectable: true });
}

async function refreshAll() {
  await loadDashboard();
  await loadBrowse();
  await loadInbox();
}

async function runSearch(query) {
  if (!query.trim()) {
    setView("recent");
    return;
  }
  const data = await api(`/api/search?q=${encodeURIComponent(query)}`);
  renderList(els.searchList, data.results || []);
  setView("search");
}

function noteFilename() {
  const raw = els.noteTitle.value.trim();
  const timestamp = new Date().toISOString().slice(0, 19).replaceAll(":", "-");
  if (raw) {
    const name = raw.endsWith(".md") ? raw : `${raw}.md`;
    return `notas/${name}`;
  }
  return `notas/nota_${timestamp}.md`;
}

function markdownNote(content) {
  const title = els.noteTitle.value.trim().replace(/\.md$/i, "") || "Nota desde telefono";
  const timestamp = new Date().toLocaleString();
  return `# ${title}\n\n- Origen: Centro web\n- Fecha: ${timestamp}\n\n${content}\n`;
}

function showQuickResult(message, timeout = 2600) {
  clearTimeout(quickResultTimer);
  els.uploadResult.textContent = message;
  if (!timeout) return;
  quickResultTimer = setTimeout(() => {
    els.uploadResult.textContent = "";
  }, timeout);
}

document.querySelector("#save-token").addEventListener("click", async () => {
  localStorage.setItem("dq_token", els.token.value.trim());
  setStatus("online", true);
  await refreshAll();
});

document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});

document.querySelector("#refresh-recent").addEventListener("click", refreshAll);
document.querySelector("#clear-search").addEventListener("click", () => {
  els.search.value = "";
  setView("recent");
});

els.browseArea.innerHTML = areas.map((area) => `<option value="${area}">${areaIcon(area)} ${areaLabel(area)}</option>`).join("");
els.browseArea.value = "documentos";
els.browseArea.addEventListener("change", () => loadBrowse());

let searchTimer = 0;
els.search.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => runSearch(els.search.value), 250);
});

els.upload.addEventListener("change", async () => {
  if (!els.upload.files.length) return;
  const file = els.upload.files[0];
  const area = file.type.startsWith("image/") ? "imagenes" : "inbox";
  const form = new FormData();
  form.append("area", area);
  form.append("file", file);
  showQuickResult("Subiendo a la PC...", 0);
  try {
    const saved = await api("/api/upload", { method: "POST", body: form });
    showQuickResult(`Guardado en PC: ${area}/${saved.path}`);
    if (area === "inbox") {
      selectedInbox = saved.path;
      setView("inbox");
    } else {
      els.browseArea.value = area;
      setView("browse");
    }
    els.upload.value = "";
    await refreshAll();
    if (area !== "inbox") await loadBrowse(area);
  } catch (error) {
    showQuickResult("No se pudo guardar. Revisa el token y la red.", 4200);
  }
});

document.querySelector("#analyze-selected").addEventListener("click", async () => {
  if (!selectedInbox) {
    renderAnalysis(null);
    return;
  }
  const form = new FormData();
  form.append("area", "inbox");
  form.append("path", selectedInbox);
  lastAnalysis = await api("/api/analyze", { method: "POST", body: form });
  renderAnalysis(lastAnalysis);
});

async function recordDecision(decision) {
  if (!lastAnalysis) return;
  const form = new FormData();
  form.append("analysis_id", lastAnalysis.id || "");
  form.append("archivo", lastAnalysis.archivo);
  form.append("decision_usuario", decision);
  form.append("categoria", lastAnalysis.categoria_sugerida);
  form.append("carpeta", lastAnalysis.carpeta_sugerida);
  form.append("confianza", String(lastAnalysis.confianza));
  form.append("explicacion", lastAnalysis.explicacion);
  await api("/api/decisions", { method: "POST", body: form });
  els.analysis.textContent = `Decision registrada: ${decision}`;
}

document.querySelector("#accept-decision").addEventListener("click", () => recordDecision("aceptado"));
document.querySelector("#reject-decision").addEventListener("click", () => recordDecision("rechazado"));

document.querySelector("#new-note-button").addEventListener("click", () => {
  els.noteSheet.classList.remove("hidden");
});

document.querySelector("#close-note").addEventListener("click", () => {
  els.noteSheet.classList.add("hidden");
});

document.querySelector("#save-note").addEventListener("click", async () => {
  const content = els.noteContent.value.trim();
  if (!content) {
    els.noteResult.textContent = "Escribe una nota primero.";
    return;
  }
  const form = new FormData();
  form.append("area", "memoria");
  form.append("path", noteFilename());
  form.append("content", markdownNote(content));
  try {
    const saved = await api("/api/docs", { method: "POST", body: form });
    els.noteResult.textContent = `Guardado en PC: memoria/${saved.path}`;
    els.noteContent.value = "";
    els.noteTitle.value = "";
    els.noteSheet.classList.add("hidden");
    showQuickResult(`Nota guardada: memoria/${saved.path}`);
    await refreshAll();
  } catch (error) {
    els.noteResult.textContent = "No se pudo guardar. Revisa el token y la red.";
  }
});

els.token.value = token();
fetch("/api/health")
  .then(() => setStatus("online", true))
  .catch(() => setStatus("offline", false));

if (token()) {
  refreshAll().catch(() => setStatus("token", false));
}
