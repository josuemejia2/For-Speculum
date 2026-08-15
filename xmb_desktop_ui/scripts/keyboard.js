import { categories, closeModule, openCurrentModule, selectCategory, selectSubmenu, state } from "./engine.js";

function wrap(index, length) {
  if (length <= 0) return 0;
  return (index + length) % length;
}

export function initializeKeyboard() {
  window.addEventListener("keydown", async (event) => {
    const module = state.currentModule;
    const submenuLength = module?.items?.length ?? 0;

    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Enter", "Escape", "Home", "End"].includes(event.key)) {
      event.preventDefault();
    }

    switch (event.key) {
      case "ArrowRight":
        await selectCategory(wrap(state.activeCategoryIndex + 1, categories.length));
        break;
      case "ArrowLeft":
        await selectCategory(wrap(state.activeCategoryIndex - 1, categories.length));
        break;
      case "ArrowDown":
        if (submenuLength) await selectSubmenu(wrap(state.activeSubmenuIndex + 1, submenuLength));
        break;
      case "ArrowUp":
        if (submenuLength) await selectSubmenu(wrap(state.activeSubmenuIndex - 1, submenuLength));
        break;
      case "Enter":
        await openCurrentModule();
        break;
      case "Escape":
        await closeModule();
        break;
      case "Home":
        await selectCategory(0);
        break;
      case "End":
        await selectCategory(categories.length - 1);
        break;
      default:
        break;
    }
  });
}
