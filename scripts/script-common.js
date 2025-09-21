// Simple animated background dots for a premium feel (no heavy libs)
(function () {
  const canvas = document.getElementById('bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let w, h, pxRatio;
  function resize() {
    pxRatio = Math.min(window.devicePixelRatio || 1, 2);
    w = canvas.clientWidth = window.innerWidth;
    h = canvas.clientHeight = window.innerHeight;
    canvas.width = Math.floor(w * pxRatio);
    canvas.height = Math.floor(h * pxRatio);
    ctx.setTransform(pxRatio, 0, 0, pxRatio, 0, 0);
  }
  window.addEventListener('resize', resize, { passive: true });
  resize();

  const DOTS = 46;
  const dots = Array.from({ length: DOTS }, () => spawn());
  function spawn() {
    const x = Math.random() * w;
    const y = Math.random() * h;
    const r = 1 + Math.random() * 2.2;
    const vx = (Math.random() - 0.5) * 0.25;
    const vy = (Math.random() - 0.5) * 0.25;
    const hueA = 260 + Math.random() * 40; // purple range
    const hueB = 160 + Math.random() * 20; // teal range
    const useA = Math.random() > 0.5;
    return { x, y, r, vx, vy, hue: useA ? hueA : hueB, a: 0.08 + Math.random() * 0.08 };
  }

  function step() {
    ctx.clearRect(0, 0, w, h);
    // Trails
    ctx.fillStyle = 'rgba(13,15,23,0.35)';
    ctx.fillRect(0, 0, w, h);

    for (const d of dots) {
      d.x += d.vx;
      d.y += d.vy;
      if (d.x < -10) d.x = w + 10; else if (d.x > w + 10) d.x = -10;
      if (d.y < -10) d.y = h + 10; else if (d.y > h + 10) d.y = -10;

      const grad = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r * 6);
      grad.addColorStop(0, `hsla(${d.hue}, 90%, 70%, ${d.a})`);
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r * 6, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(step);
  }
  step();
})();

// Footer year
document.getElementById('year').textContent = new Date().getFullYear();

// Background audio controller (local mp3 only)
(function () {
  const audio = document.getElementById('bg-audio');
  const toggle = document.getElementById('audio-toggle');
  if (!audio || !toggle) return;

  const START_AT = 0; // start from the beginning
  const FADE_MS = 1200; // fade-in duration
  const DEFAULT_VOLUME = 0.5;

  // UI state
  // Start disabled by default; require an explicit click to play
  let enabled = false;
  function updateUI() {
    toggle.classList.toggle('on', enabled);
    toggle.classList.toggle('off', !enabled);
    toggle.setAttribute('aria-pressed', String(enabled));
  }

  // Helpers
  let fadeRAF = null;
  function cancelFade() { if (fadeRAF) cancelAnimationFrame(fadeRAF); fadeRAF = null; }
  function fadeTo(vol, ms = FADE_MS) {
    cancelFade();
    const start = performance.now();
    const from = audio.volume;
    const to = Math.max(0, Math.min(1, vol));
    function tick(t) {
      const k = Math.min(1, (t - start) / ms);
      const eased = k * (2 - k);
      audio.volume = from + (to - from) * eased;
      if (k < 1) fadeRAF = requestAnimationFrame(tick);
    }
    fadeRAF = requestAnimationFrame(tick);
  }
  function ensureStartOffset() {
    const seek = () => {
      try { audio.currentTime = START_AT; } catch (_) {}
    };
    if (audio.readyState >= 1) seek(); else audio.addEventListener('loadedmetadata', seek, { once: true });
  }

  function applyState() {
    if (!enabled) {
      cancelFade();
      audio.pause();
      audio.muted = true;
    }
    updateUI();
  }

  // Initialize
  audio.muted = true; // keep muted until user clicks
  applyState();

  toggle.addEventListener('click', async () => {
    enabled = !enabled;
    if (enabled) {
      ensureStartOffset(); // will set to 0
      audio.muted = false;
      audio.volume = 0;
      try {
        await audio.play();
        fadeTo(DEFAULT_VOLUME, FADE_MS);
      } catch (_) {
        // If playback fails, revert UI state
        enabled = false;
      }
    } else {
      cancelFade();
      audio.pause();
      audio.muted = true;
    }
    updateUI();
  });

  // Remove global gesture-based auto-start; playback only starts via the toggle click
})();
