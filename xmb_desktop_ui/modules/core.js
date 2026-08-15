const views = [
  {
    focus: "Engine Monitor",
    description: "Supervision de procesos, rendimiento y salud del nucleo visual.",
    metrics: [
      { label: "Core", value: "Stable" },
      { label: "Load", value: "24%" },
      { label: "Frame", value: "60" },
    ],
  },
  {
    focus: "Connectivity",
    description: "Espacio para conexiones locales, API, sockets y rutas internas.",
    metrics: [
      { label: "Local", value: "On" },
      { label: "API", value: "Slot" },
      { label: "Bridge", value: "Open" },
    ],
  },
  {
    focus: "Power Mode",
    description: "Control conceptual para perfiles de energia, animacion y rendimiento.",
    metrics: [
      { label: "Mode", value: "Fluid" },
      { label: "Heat", value: "Low" },
      { label: "Motion", value: "On" },
    ],
  },
];

export default {
  title: "Core Systems",
  subtitle: "Motores, rendimiento y base del escritorio.",
  status: "OPTIMIZED",
  items: [
    { code: "01", title: "Engine Monitor", subtitle: "Salud del nucleo." },
    { code: "02", title: "Connectivity", subtitle: "Rutas y enlaces." },
    { code: "03", title: "Power Mode", subtitle: "Perfil visual." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "CORE",
      title: this.title,
      subtitle: isOpen ? "Control expandido del motor principal." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: [
        {
          kicker: "Runtime",
          header: "Shell Engine",
          description: "El motor separa estado, render y entrada para escalar sin romper la interfaz.",
          footnote: "scripts/engine.js",
        },
        {
          kicker: "Input",
          header: "Keyboard Layer",
          description: "Flechas, Enter y Escape se procesan en una capa independiente.",
          footnote: "scripts/keyboard.js",
        },
        {
          kicker: "Motion",
          header: "Animation Layer",
          description: "La escena respira con canvas ambiental y transiciones de foco.",
          footnote: "scripts/animationController.js",
        },
      ],
    };
  },
};
