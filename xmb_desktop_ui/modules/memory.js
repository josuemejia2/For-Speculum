const views = [
  {
    focus: "Archive Index",
    description: "Indice visual para documentos, sesiones, bitacora y recursos.",
    metrics: [
      { label: "Vault", value: "On" },
      { label: "Index", value: "Hot" },
      { label: "Recall", value: "Fast" },
    ],
  },
  {
    focus: "Recall Engine",
    description: "Buscador conceptual para recuperar contexto y fragmentos importantes.",
    metrics: [
      { label: "Query", value: "Ready" },
      { label: "Cache", value: "Warm" },
      { label: "Rank", value: "Smart" },
    ],
  },
  {
    focus: "Data Cache",
    description: "Control de estados temporales, salidas generadas y vistas recientes.",
    metrics: [
      { label: "Temp", value: "Clean" },
      { label: "TTL", value: "Auto" },
      { label: "Store", value: "Local" },
    ],
  },
];

export default {
  title: "Memory Vault",
  subtitle: "Memoria, archivo y restauracion de contexto.",
  status: "STABLE",
  items: [
    { code: "01", title: "Archive Index", subtitle: "Archivo general." },
    { code: "02", title: "Recall Engine", subtitle: "Recuperacion." },
    { code: "03", title: "Data Cache", subtitle: "Estados temporales." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "MEMORY",
      title: this.title,
      subtitle: isOpen ? "Vista profunda de memoria y archivo." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: [
        {
          kicker: "Archive",
          header: "Document Spine",
          description: "La memoria puede crecer por areas sin cambiar el shell visual.",
          footnote: "Local-first structure.",
        },
        {
          kicker: "Recall",
          header: "Context Snapshots",
          description: "Cada modulo puede guardar y restaurar su propio estado.",
          footnote: "State-friendly design.",
        },
        {
          kicker: "Cache",
          header: "Session Memory",
          description: "Ideal para vistas recientes, simuladores y resultados temporales.",
          footnote: "Ready for persistence.",
        },
      ],
    };
  },
};
