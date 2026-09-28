import { bootstrapShell } from "./scripts/app.js";

window.addEventListener("DOMContentLoaded", () => {
  bootstrapShell().catch((error) => {
    console.error("PS3 shell initialization failed:", error);
  });
});
