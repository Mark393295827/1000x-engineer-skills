/**
 * 1000x Engineer: Autonomous Software Factory
 * Cinematic Interactive Promotional Animation Engine
 */

class PromoAnimationEngine {
  constructor() {
    this.currentScene = 0;
    this.totalScenes = 7;
    this.isPlaying = true;
    this.autoPlayInterval = null;
    this.sceneDuration = 6000; // 6 seconds per scene
    this.audioEnabled = false;
    this.audioCtx = null;
    this.activeSimTimeouts = [];

    this.initCanvas();
    this.initAudio();
    this.initUI();
    this.initKeyboard();
    this.initTouch();
    this.startAutoPlay();
    this.animateMultiplier();
  }

  /* -------------------------------------------------------------
     1. Web Audio API Procedural SFX Synthesizer
     ------------------------------------------------------------- */
  initAudio() {
    const audioBtn = document.getElementById('btn-audio');
    if (!audioBtn) return;

    audioBtn.addEventListener('click', () => {
      if (!this.audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioCtx = new AudioContext();
      }
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      this.audioEnabled = !this.audioEnabled;
      audioBtn.textContent = this.audioEnabled ? '🔊 SFX: ON' : '🔇 SFX: OFF';
      audioBtn.classList.toggle('active', this.audioEnabled);
      if (this.audioEnabled) this.playTone(880, 'sine', 0.1, 0.1);
    });
  }

  playTone(freq, type = 'sine', duration = 0.15, volume = 0.05) {
    if (!this.audioEnabled || !this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
      gain.gain.setValueAtTime(volume, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + duration);
    } catch (e) {
      console.warn('Audio error:', e);
    }
  }

  playSwoosh() {
    if (!this.audioEnabled || !this.audioCtx) return;
    this.playTone(300, 'triangle', 0.2, 0.04);
    setTimeout(() => this.playTone(600, 'sine', 0.3, 0.06), 80);
  }

  playSuccessChime() {
    if (!this.audioEnabled || !this.audioCtx) return;
    [523.25, 659.25, 783.99, 1046.50].forEach((f, i) => {
      setTimeout(() => this.playTone(f, 'sine', 0.4, 0.05), i * 90);
    });
  }

  /* -------------------------------------------------------------
     2. Interactive Particle Matrix Canvas (HiDPI Scaled)
     ------------------------------------------------------------- */
  initCanvas() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = 0;
    let height = 0;
    let dpr = window.devicePixelRatio || 1;

    const resize = () => {
      dpr = window.devicePixelRatio || 1;
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener('resize', resize);

    const particles = [];
    const numParticles = Math.min(80, Math.floor(width / 18));

    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        radius: Math.random() * 2 + 1,
        color: Math.random() > 0.4 ? 'rgba(0, 240, 255, ' : 'rgba(255, 170, 0, '
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Cyberpunk Grid lines
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.03)';
      ctx.lineWidth = 1;
      const gridSize = 60;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw & link particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.fillStyle = p.color + '0.6)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 130) {
            ctx.strokeStyle = `rgba(0, 240, 255, ${0.15 * (1 - dist / 130)})`;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(render);
    };

    render();
  }

  /* -------------------------------------------------------------
     3. Scene Navigation & Timeline Scrubber
     ------------------------------------------------------------- */
  initUI() {
    this.scenes = document.querySelectorAll('.scene');
    this.navPills = document.querySelectorAll('.nav-pill');
    this.progressBar = document.getElementById('progress-fill');
    this.progressTrack = document.getElementById('progress-track');
    this.playBtn = document.getElementById('btn-play');
    this.prevBtn = document.getElementById('btn-prev');
    this.nextBtn = document.getElementById('btn-next');

    this.navPills.forEach((pill, idx) => {
      pill.addEventListener('click', () => {
        this.goToScene(idx);
        this.pauseAutoPlay();
      });
    });

    if (this.playBtn) {
      this.playBtn.addEventListener('click', () => {
        if (this.isPlaying) {
          this.pauseAutoPlay();
        } else {
          this.startAutoPlay();
        }
      });
    }

    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => {
        this.goToScene((this.currentScene - 1 + this.totalScenes) % this.totalScenes);
        this.pauseAutoPlay();
      });
    }

    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', () => {
        this.goToScene((this.currentScene + 1) % this.totalScenes);
        this.pauseAutoPlay();
      });
    }

    if (this.progressTrack) {
      this.progressTrack.addEventListener('click', (e) => {
        const rect = this.progressTrack.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        const target = Math.min(this.totalScenes - 1, Math.max(0, Math.floor(pos * this.totalScenes)));
        this.goToScene(target);
        this.pauseAutoPlay();
      });
    }

    // Interactive simulator in Scene 7
    const simBtn = document.getElementById('btn-run-sim');
    const resetBtn = document.getElementById('btn-reset-sim');
    const simOutput = document.getElementById('sim-terminal-output');
    const cliInput = document.getElementById('cli-input');
    const presetButtons = document.querySelectorAll('.btn-preset');

    if (simBtn && simOutput) {
      simBtn.addEventListener('click', () => {
        const customTask = cliInput && cliInput.value.trim() ? cliInput.value.trim() : 'Full-Stack Autonomous SOP';
        this.runSimulation(simOutput, customTask);
      });
    }

    if (resetBtn && simOutput) {
      resetBtn.addEventListener('click', () => {
        this.clearSimTimeouts();
        simOutput.innerHTML = '<div style="color:var(--text-muted);">Terminal reset. Choose a preset or click "Run Autonomous SOP"...</div>';
        const badge = document.getElementById('sim-status-badge');
        if (badge) {
          badge.textContent = '● READY';
          badge.style.color = 'var(--neon-green)';
        }
        if (cliInput) cliInput.value = '';
      });
    }

    presetButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const taskType = btn.getAttribute('data-task');
        let taskName = 'Autonomous Refactor';
        if (taskType === 'auth-refactor') taskName = 'Decompose Legacy Auth Monolith (MECE)';
        if (taskType === 'security-fix') taskName = 'SOC2 / Zero-CVE AST Remediation';
        if (taskType === 'e2e-matrix') taskName = 'Full E2E Playwright Matrix Verification';
        if (cliInput) cliInput.value = taskName;
        if (simOutput) this.runSimulation(simOutput, taskName);
      });
    });

    if (cliInput && simOutput) {
      cliInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const taskName = cliInput.value.trim() || 'Custom Pipeline Task';
          this.runSimulation(simOutput, taskName);
        }
      });
    }
  }

  /* -------------------------------------------------------------
     4. Keyboard Navigation & Shortcuts
     ------------------------------------------------------------- */
  initKeyboard() {
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        this.isPlaying ? this.pauseAutoPlay() : this.startAutoPlay();
      } else if (e.code === 'ArrowRight' || e.code === 'KeyD') {
        this.goToScene((this.currentScene + 1) % this.totalScenes);
        this.pauseAutoPlay();
      } else if (e.code === 'ArrowLeft' || e.code === 'KeyA') {
        this.goToScene((this.currentScene - 1 + this.totalScenes) % this.totalScenes);
        this.pauseAutoPlay();
      } else if (e.code === 'KeyM') {
        document.getElementById('btn-audio')?.click();
      } else if (e.key >= '1' && e.key <= '7') {
        this.goToScene(parseInt(e.key, 10) - 1);
        this.pauseAutoPlay();
      } else if ((e.code === 'Enter' || e.code === 'KeyR') && this.currentScene === 6) {
        document.getElementById('btn-run-sim')?.click();
      }
    });
  }

  /* -------------------------------------------------------------
     5. Mobile Touch Gestures
     ------------------------------------------------------------- */
  initTouch() {
    let touchStartX = 0;
    let touchStartY = 0;

    document.addEventListener(
      'touchstart',
      (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
      },
      { passive: true }
    );

    document.addEventListener(
      'touchend',
      (e) => {
        const touchEndX = e.changedTouches[0].screenX;
        const touchEndY = e.changedTouches[0].screenY;
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;

        if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
          if (deltaX < 0) {
            this.goToScene((this.currentScene + 1) % this.totalScenes);
          } else {
            this.goToScene((this.currentScene - 1 + this.totalScenes) % this.totalScenes);
          }
          this.pauseAutoPlay();
        }
      },
      { passive: true }
    );
  }

  goToScene(index) {
    this.scenes.forEach((s) => s.classList.remove('active'));
    this.navPills.forEach((p) => p.classList.remove('active'));

    this.currentScene = index;
    if (this.scenes[index]) this.scenes[index].classList.add('active');
    if (this.navPills[index]) this.navPills[index].classList.add('active');

    if (this.progressBar) {
      const pct = ((index + 1) / this.totalScenes) * 100;
      this.progressBar.style.width = `${pct}%`;
    }

    this.playSwoosh();

    if (index === 1) this.animateMultiplier();
    if (index === 4) this.playSuccessChime();
  }

  startAutoPlay() {
    this.isPlaying = true;
    if (this.playBtn) this.playBtn.textContent = '⏸ Pause';
    clearInterval(this.autoPlayInterval);
    this.autoPlayInterval = setInterval(() => {
      const next = (this.currentScene + 1) % this.totalScenes;
      this.goToScene(next);
    }, this.sceneDuration);
  }

  pauseAutoPlay() {
    this.isPlaying = false;
    if (this.playBtn) this.playBtn.textContent = '▶ Play';
    clearInterval(this.autoPlayInterval);
  }

  /* -------------------------------------------------------------
     6. Dynamic Visual Effects & Counters
     ------------------------------------------------------------- */
  animateMultiplier() {
    const el = document.getElementById('multiplier-counter');
    if (!el) return;
    let val = 1;
    const targets = [1, 10, 100, 500, 1000];
    let step = 0;

    const interval = setInterval(() => {
      if (step < targets.length) {
        val = targets[step];
        el.textContent = `${val}x`;
        this.playTone(200 + step * 180, 'sawtooth', 0.1, 0.04);
        step++;
      } else {
        clearInterval(interval);
      }
    }, 280);
  }

  clearSimTimeouts() {
    this.activeSimTimeouts.forEach((t) => clearTimeout(t));
    this.activeSimTimeouts = [];
  }

  runSimulation(outputEl, taskTitle = 'Full-Stack Autonomous SOP') {
    this.clearSimTimeouts();
    outputEl.innerHTML = '';

    const badge = document.getElementById('sim-status-badge');
    const updateBadge = (status, color) => {
      if (badge) {
        badge.textContent = `● ${status}`;
        badge.style.color = color;
      }
    };

    updateBadge('PREFLIGHT', 'var(--neon-amber)');

    const steps = [
      {
        text: `[1/5] 🔍 PREFLIGHT: Task "${taskTitle}" initialized. Git SHA verified, workspace clean.`,
        color: '#00f0ff',
        status: 'PREFLIGHT',
        statusColor: 'var(--neon-amber)',
      },
      {
        text: `[2/5] 📝 CONTRACT: Strict schema validated (task-contract.schema.json). 0 mutable leaks.`,
        color: '#00f0ff',
        status: 'CONTRACTED',
        statusColor: 'var(--neon-amber)',
      },
      {
        text: `[3/5] 🛡️ EVALS FIRST: Grader manifest loaded (48 unit, 12 property, 8 E2E gates).`,
        color: '#00f0ff',
        status: 'EVAL_READY',
        statusColor: 'var(--neon-amber)',
      },
      {
        text: `[4/5] ⚡ EXECUTING: Routing T0 tools (linters), T1 fast agents (routes), T3 reasoning (invariants).`,
        color: '#ffb86c',
        status: 'EXECUTING',
        statusColor: '#0077ff',
      },
      {
        text: `     > T1 Worker #1: Scaffolding database migrations (0.6s)`,
        color: '#00f0ff',
        status: 'EXECUTING',
        statusColor: '#0077ff',
      },
      {
        text: `     > T3 Reasoner #2: Verifying lock order inversion & deadlock freedom (1.2s)`,
        color: '#ffb86c',
        status: 'EXECUTING',
        statusColor: '#0077ff',
      },
      {
        text: `     > T0 Graders: 68/68 test assertions executed in sandboxed isolation.`,
        color: '#00f0ff',
        status: 'VERIFYING',
        statusColor: '#ffb86c',
      },
      {
        text: `[5/5] 📜 RECEIPT & SKILLIFY: RUN_RECEIPT.json + sha256 emitted. STATUS: 100% PASS ✅`,
        color: '#00ff88',
        status: 'ACCEPTED',
        statusColor: 'var(--neon-green)',
      },
    ];

    steps.forEach((step, i) => {
      const timeout = setTimeout(() => {
        updateBadge(step.status, step.statusColor);
        const div = document.createElement('div');
        div.textContent = step.text;
        div.style.color = step.color;
        outputEl.appendChild(div);
        outputEl.scrollTop = outputEl.scrollHeight;
        this.playTone(380 + i * 75, 'sine', 0.08, 0.03);
        if (i === steps.length - 1) this.playSuccessChime();
      }, i * 320);
      this.activeSimTimeouts.push(timeout);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.promoApp = new PromoAnimationEngine();
});
