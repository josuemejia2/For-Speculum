import { installAnimations, startAmbientCanvas, startClock } from "./animationController.js";
import { preloadModules, render } from "./engine.js";
import { initializeKeyboard } from "./keyboard.js";

export async function bootstrapShell() {
  installAnimations();
  startAmbientCanvas();
  startClock();
  initializeKeyboard();
  await preloadModules();
  await render();
}
