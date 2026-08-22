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

    this.initCanvas();
    this.initAudio();
    this.initUI();
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
     2. Interactive Particle Matrix Canvas
     ------------------------------------------------------------- */
  initCanvas() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

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

    // Interactive simulator trigger in Scene 7
    const simBtn = document.getElementById('btn-run-sim');
    const simOutput = document.getElementById('sim-terminal-output');
    if (simBtn && simOutput) {
      simBtn.addEventListener('click', () => {
        this.runSimulation(simOutput);
      });
    }
  }

  goToScene(index) {
    this.scenes.forEach(s => s.classList.remove('active'));
    this.navPills.forEach(p => p.classList.remove('active'));

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
     4. Dynamic Visual Effects & Counters
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

  runSimulation(outputEl) {
    outputEl.innerHTML = '';
    const logs = [
      '[1/5] 🔍 Forward Deploy: Capturing live environment traces...',
      '[2/5] 📝 Skills as Code: Validating Markdown contract schema...',
      '[3/5] 🛡️ Evals First: Launching isolated test harness (50 tests)...',
      '[4/5] ⚡ Autonomous Loop: Dispatching parallel subagents...',
      '     > Subagent #1 (Flash): Database migration generated (0.8s)',
      '     > Subagent #2 (Thinking): Lock concurrency verified (1.4s)',
      '     > Subagent #3 (Flash): 12 API route contracts created (0.9s)',
      '[5/5] 📜 Audit Receipt: RUN_RECEIPT.md compiled. STATUS: 100% PASS ✅'
    ];

    logs.forEach((line, i) => {
      setTimeout(() => {
        const div = document.createElement('div');
        div.textContent = line;
        div.style.color = line.includes('PASS') ? '#00ff88' : '#00f0ff';
        outputEl.appendChild(div);
        outputEl.scrollTop = outputEl.scrollHeight;
        this.playTone(400 + i * 80, 'sine', 0.08, 0.03);
        if (i === logs.length - 1) this.playSuccessChime();
      }, i * 350);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.promoApp = new PromoAnimationEngine();
});
