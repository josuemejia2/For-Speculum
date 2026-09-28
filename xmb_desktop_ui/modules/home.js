const views = [
  {
    focus: "Nexus",
    description: "Centro de entrada con estado del shell, accesos vivos y presencia del sistema.",
    metrics: [
      { label: "Flow", value: "98%" },
      { label: "Mode", value: "Live" },
      { label: "Sync", value: "Ready" },
    ],
    cards: [
      {
        kicker: "Pulse",
        header: "Live Surface",
        description: "La escena responde a navegacion, foco y apertura de modulos.",
        footnote: "Foundation layer active.",
      },
      {
        kicker: "Quick Entry",
        header: "Dynamic Modules",
        description: "Cada categoria carga su modulo de forma dinamica.",
        footnote: "Expansion slots available.",
      },
      {
        kicker: "Presence",
        header: "Quiet OS",
        description: "Un escritorio inmersivo con lectura simple y sin ruido visual.",
        footnote: "Designed as an OS shell.",
      },
    ],
  },
  {
    focus: "Launch Rail",
    description: "Linea horizontal estilo XMB para saltar entre areas sin perder contexto.",
    metrics: [
      { label: "Route", value: "6" },
      { label: "Latency", value: "Low" },
      { label: "Input", value: "Keys" },
    ],
    cards: [
      {
        kicker: "Categories",
        header: "Horizontal Rail",
        description: "HOME, CORE, AI, MEMORY, LOGS y SYSTEM viven como modulos separados.",
        footnote: "Clean navigation map.",
      },
      {
        kicker: "Submenus",
        header: "Vertical Focus",
        description: "Cada categoria despliega una columna vertical con foco persistente.",
        footnote: "XMB behavior.",
      },
      {
        kicker: "Open State",
        header: "Depth Layer",
        description: "Enter abre una vista mas profunda sin cambiar de pantalla.",
        footnote: "Smooth depth model.",
      },
    ],
  },
  {
    focus: "Signal Feed",
    description: "Panel reservado para notificaciones del sistema y estados de actividad.",
    metrics: [
      { label: "Alerts", value: "0" },
      { label: "Noise", value: "Low" },
      { label: "Queue", value: "Clear" },
    ],
    cards: [
      {
        kicker: "Activity",
        header: "Event Slots",
        description: "Eventos del shell pueden entrar aqui como mensajes compactos.",
        footnote: "Future event bridge.",
      },
      {
        kicker: "Focus",
        header: "Signal Filter",
        description: "El sistema evita saturar la pantalla principal.",
        footnote: "Minimal by design.",
      },
      {
        kicker: "Status",
        header: "Ambient State",
        description: "Lecturas cortas y visuales para mantener fluidez.",
        footnote: "Ambient monitoring.",
      },
    ],
  },
];

export default {
  title: "Home Nexus",
  subtitle: "Entrada principal del escritorio modular.",
  status: "READY",
  items: [
    { code: "01", title: "Nexus", subtitle: "Estado y presencia." },
    { code: "02", title: "Launch Rail", subtitle: "Accesos principales." },
    { code: "03", title: "Signal Feed", subtitle: "Lectura de actividad." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "HOME",
      title: this.title,
      subtitle: isOpen ? "Vista expandida del punto de entrada." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: view.cards.map((card) => ({
        ...card,
        description: isOpen ? `${card.description} Preparado para conectar acciones reales.` : card.description,
      })),
    };
  },
};
