export function installAnimations() {
  requestAnimationFrame(() => {
    document.body.classList.add("scene-ready");
  });
}

export function pulseModuleStage() {
  const modulePanel = document.querySelector(".module-panel");
  if (!modulePanel) return;

  modulePanel.classList.remove("pulse-state");
  void modulePanel.offsetWidth;
  modulePanel.classList.add("pulse-state");
}

export function startClock() {
  const clock = document.querySelector("#clock-readout");
  if (!clock) return;

  const tick = () => {
    const now = new Date();
    clock.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  tick();
  window.setInterval(tick, 1000);
}

export function startAmbientCanvas() {
  const canvas = document.querySelector("#ambient-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const particles = Array.from({ length: 72 }, (_, index) => ({
    x: Math.random(),
    y: Math.random(),
    speed: 0.00035 + Math.random() * 0.00075,
    size: 0.7 + Math.random() * 1.9,
    phase: index * 0.37,
  }));

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(now) {
    const width = window.innerWidth;
    const height = window.innerHeight;
    ctx.clearRect(0, 0, width, height);

    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, "rgba(98, 225, 255, 0.08)");
    gradient.addColorStop(0.45, "rgba(120, 106, 255, 0.03)");
    gradient.addColorStop(1, "rgba(12, 18, 35, 0.02)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(120, 230, 255, 0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 7; i += 1) {
      const y = ((now * 0.018 + i * 150) % (height + 220)) - 110;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.bezierCurveTo(width * 0.3, y - 52, width * 0.62, y + 64, width, y - 12);
      ctx.stroke();
    }

    particles.forEach((particle) => {
      particle.y -= particle.speed * 16;
      if (particle.y < -0.05) {
        particle.y = 1.05;
        particle.x = Math.random();
      }

      const pulse = 0.55 + Math.sin(now * 0.002 + particle.phase) * 0.45;
      ctx.fillStyle = `rgba(190, 245, 255, ${0.22 + pulse * 0.3})`;
      ctx.beginPath();
      ctx.arc(particle.x * width, particle.y * height, particle.size + pulse, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(draw);
  }

  resize();
  window.addEventListener("resize", resize);
  requestAnimationFrame(draw);
}
