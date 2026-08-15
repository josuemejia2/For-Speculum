import { createCategoryButton, createModuleView, createSubmenuItem } from "../components/ui.js";
import { pulseModuleStage } from "./animationController.js";

export const categories = [
  { id: "home", label: "HOME", module: "home", icon: "H" },
  { id: "core", label: "CORE", module: "core", icon: "C" },
  { id: "ai", label: "AI", module: "ai", icon: "AI" },
  { id: "memory", label: "MEMORY", module: "memory", icon: "M" },
  { id: "logs", label: "LOGS", module: "logs", icon: "L" },
  { id: "system", label: "SYSTEM", module: "system", icon: "S" },
];

export const state = {
  activeCategoryIndex: 0,
  activeSubmenuIndex: 0,
  isModuleOpen: false,
  currentModule: null,
  loadedModules: {},
  route: "HOME / Nexus",
};

export const elements = {
  categoryBar: document.querySelector(".category-ribbon"),
  submenuPanel: document.querySelector(".submenu-panel"),
  modulePanel: document.querySelector(".module-panel"),
  activePath: document.querySelector("#active-path"),
  moduleStatus: document.querySelector("#module-status"),
};

function clampIndex(index, max) {
  if (max < 0) return 0;
  return Math.max(0, Math.min(index, max));
}

function activeCategory() {
  return categories[state.activeCategoryIndex];
}

export async function loadModule(name) {
  if (state.loadedModules[name]) {
    return state.loadedModules[name];
  }

  const module = await import(`../modules/${name}.js`);
  state.loadedModules[name] = module.default;
  return module.default;
}

export async function preloadModules() {
  await Promise.all(categories.map((category) => loadModule(category.module)));
}

export function updateSystemReadout() {
  const category = activeCategory();
  const item = state.currentModule?.items?.[state.activeSubmenuIndex];
  const path = `${category.label} / ${item?.title ?? "Nexus"}`;
  state.route = path;
  if (elements.activePath) elements.activePath.textContent = path;
  if (elements.moduleStatus) elements.moduleStatus.textContent = state.currentModule?.status ?? "READY";
}

export function renderCategories() {
  elements.categoryBar.innerHTML = "";
  categories.forEach((category, index) => {
    const button = createCategoryButton(category, index === state.activeCategoryIndex);
    button.addEventListener("click", () => selectCategory(index));
    elements.categoryBar.appendChild(button);
  });

  const active = elements.categoryBar.querySelector(".category-item.active");
  active?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
}

export async function renderSubmenu() {
  elements.submenuPanel.innerHTML = "";
  const module = await loadModule(activeCategory().module);
  state.currentModule = module;
  state.activeSubmenuIndex = clampIndex(state.activeSubmenuIndex, module.items.length - 1);

  module.items.forEach((item, index) => {
    const submenuItem = createSubmenuItem(item, index === state.activeSubmenuIndex);
    submenuItem.addEventListener("click", () => selectSubmenu(index));
    elements.submenuPanel.appendChild(submenuItem);
  });
}

export function renderModulePanel() {
  elements.modulePanel.innerHTML = "";
  if (!state.currentModule) return;

  const payload = state.currentModule.render(state.activeSubmenuIndex, state.isModuleOpen);
  elements.modulePanel.appendChild(createModuleView(payload, state.isModuleOpen));
  pulseModuleStage();
  updateSystemReadout();
}

export async function selectCategory(index) {
  state.activeCategoryIndex = clampIndex(index, categories.length - 1);
  state.activeSubmenuIndex = 0;
  state.isModuleOpen = false;
  await render();
}

export async function selectSubmenu(index) {
  const max = state.currentModule?.items?.length ? state.currentModule.items.length - 1 : 0;
  state.activeSubmenuIndex = clampIndex(index, max);
  state.isModuleOpen = false;
  await render();
}

export async function openCurrentModule() {
  if (!state.currentModule) return;
  state.currentModule.activate?.(state.activeSubmenuIndex);
  state.isModuleOpen = true;
  await render();
}

export async function closeModule() {
  state.isModuleOpen = false;
  await render();
}

export async function render() {
  renderCategories();
  await renderSubmenu();
  renderModulePanel();
}
