const views = [
  {
    focus: "Agent Hub",
    description: "Zona para agentes, asistentes especializados y perfiles de inteligencia.",
    metrics: [
      { label: "Agents", value: "3" },
      { label: "Mode", value: "Assist" },
      { label: "Guard", value: "On" },
    ],
  },
  {
    focus: "Inference Lab",
    description: "Espacio para simulaciones, lectura de escenarios y experimentos.",
    metrics: [
      { label: "Runs", value: "12" },
      { label: "Depth", value: "Med" },
      { label: "Trace", value: "Clean" },
    ],
  },
  {
    focus: "Prompt Studio",
    description: "Banco modular para crear instrucciones reutilizables del sistema.",
    metrics: [
      { label: "Sets", value: "8" },
      { label: "Reuse", value: "High" },
      { label: "Drift", value: "Low" },
    ],
  },
];

export default {
  title: "AI Core",
  subtitle: "Inteligencia, razonamiento y configuracion de agentes.",
  status: "AUTONOMOUS",
  items: [
    { code: "01", title: "Agent Hub", subtitle: "Asistentes vivos." },
    { code: "02", title: "Inference Lab", subtitle: "Simulaciones." },
    { code: "03", title: "Prompt Studio", subtitle: "Plantillas." },
  ],
  render(activeIndex, isOpen) {
    const view = views[activeIndex] ?? views[0];
    return {
      kicker: "AI",
      title: this.title,
      subtitle: isOpen ? "Capa AI expandida para automatizaciones futuras." : this.subtitle,
      status: this.status,
      focus: view.focus,
      description: view.description,
      metrics: view.metrics,
      cards: [
        {
          kicker: "Reasoning",
          header: "Context Engine",
          description: "Preparado para cargar contexto por modulo sin mezclar responsabilidades.",
          footnote: "Future connector slot.",
        },
        {
          kicker: "Control",
          header: "Persona Matrix",
          description: "Cada perfil puede tener reglas, memoria y acciones propias.",
          footnote: "Expandable agent pattern.",
        },
        {
          kicker: "Safety",
          header: "Custody Gate",
          description: "Antes de ejecutar acciones sensibles, el sistema puede pedir confirmacion.",
          footnote: "Human-in-the-loop ready.",
        },
      ],
    };
  },
};
