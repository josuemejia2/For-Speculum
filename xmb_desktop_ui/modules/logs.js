const views = [
  {
    focus: "Event Stream",
    description: "Linea de eventos para cambios de estado, aperturas y acciones.",
    metrics: [
      { label: "Events", value: "Live" },
      { label: "Rate", value: "Soft" },
      { label: "Trace", value: "On" },
    ],
  },
  {
    focus: "Security Feed",
    description: "Canal reservado para alertas, permisos y decisiones sensibles.",
    metrics: [
      { label: "Alerts", value: "0" },
      { label: "Auth", value: "Local" },
      { label: "Risk", value: "Low" },
    ],
  },
  {
    focus: "Performance Trace",
    description: "Lectura de fluidez, render y latencia del entorno.",
    metrics: [
      { label: "FPS", value: "60" },
      { label: "Paint", value: "Smooth" },
      { label: "Input", value: "Direct" },
    ],
  },
];

export default {
  title: "Live Logs",
  subtitle: "Eventos, auditoria y telemetria del shell.",
  status: "MONITORING",
  items: [
    { code: "01", title: "Event Stream", subtitle: "Cambios vivos." },
    { code: "02", title: "Security Feed", subtitle: "Alertas." },
    { code: "03", title: "Performance Trace", subtitle: "Rendimiento." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "LOGS",
      title: this.title,
      subtitle: isOpen ? "Panel expandido para lectura historica." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: [
        {
          kicker: "Events",
          header: "State Timeline",
          description: "Navegacion, carga de modulos y acciones pueden registrarse aqui.",
          footnote: "Observable shell.",
        },
        {
          kicker: "Audit",
          header: "Action Ledger",
          description: "Un lugar natural para guardar acciones importantes del usuario.",
          footnote: "Human-readable logs.",
        },
        {
          kicker: "Perf",
          header: "Motion Trace",
          description: "La capa visual puede medir su fluidez sin invadir la experiencia.",
          footnote: "Future metric slot.",
        },
      ],
    };
  },
};
