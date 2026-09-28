const views = [
  {
    focus: "Display Mode",
    description: "Control de brillo, profundidad, desenfoque y densidad visual.",
    metrics: [
      { label: "Theme", value: "Dark" },
      { label: "Glass", value: "On" },
      { label: "Glow", value: "Soft" },
    ],
  },
  {
    focus: "Audio Engine",
    description: "Espacio preparado para sonidos de foco, alerta y entrada.",
    metrics: [
      { label: "Sound", value: "Slot" },
      { label: "Alert", value: "Calm" },
      { label: "Mix", value: "Ready" },
    ],
  },
  {
    focus: "Shell Settings",
    description: "Preferencias del escritorio, arquitectura y expansion futura.",
    metrics: [
      { label: "Scale", value: "Auto" },
      { label: "Layout", value: "XMB" },
      { label: "Build", value: "01" },
    ],
  },
];

export default {
  title: "System Matrix",
  subtitle: "Configuracion global del entorno operativo.",
  status: "ONLINE",
  items: [
    { code: "01", title: "Display Mode", subtitle: "Visuales." },
    { code: "02", title: "Audio Engine", subtitle: "Sonido." },
    { code: "03", title: "Shell Settings", subtitle: "Preferencias." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "SYSTEM",
      title: this.title,
      subtitle: isOpen ? "Configuracion expandida del sistema." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: [
        {
          kicker: "Display",
          header: "Adaptive Interface",
          description: "El layout responde a escritorio y movil sin perder identidad XMB.",
          footnote: "Responsive shell.",
        },
        {
          kicker: "Modules",
          header: "Expansion Contract",
          description: "Cada modulo exporta items y render; el motor se mantiene estable.",
          footnote: "Drop-in modules.",
        },
        {
          kicker: "System",
          header: "Route /PS3",
          description: "El shell vive separado del laboratorio visual y puede evolucionar aparte.",
          footnote: "Independent surface.",
        },
      ],
    };
  },
};
