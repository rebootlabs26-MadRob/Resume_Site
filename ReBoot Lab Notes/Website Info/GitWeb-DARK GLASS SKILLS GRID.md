<!-- DARK GLASS SKILLS GRID -->
<section id="skills" class="fade-in">
  <h2>Skills Matrix</h2>

  <div class="skills-grid glass">

    <!-- Python -->
    <div class="skill-card glass">
      <div class="skill-title">Python</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- JavaScript -->
    <div class="skill-card glass">
      <div class="skill-title">JavaScript</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- C / C-Style -->
    <div class="skill-card glass">
      <div class="skill-title">C / C-Style Logic</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- HTML -->
    <div class="skill-card glass">
      <div class="skill-title">HTML</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- CSS -->
    <div class="skill-card glass">
      <div class="skill-title">CSS</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-4"></div>
      </div>
      <div class="skill-level">Intermediate‑Plus</div>
    </div>

    <!-- Markdown -->
    <div class="skill-card glass">
      <div class="skill-title">Markdown</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- Bash -->
    <div class="skill-card glass">
      <div class="skill-title">Bash / Shell</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-2"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- YAML -->
    <div class="skill-card glass">
      <div class="skill-title">YAML / Config</div>
      <div class="skill-bar glass-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

  </div>
</section>

<style>
  /* GRID LAYOUT */
  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.4rem;
    margin-top: 1.4rem;
  }

  /* GLASS EFFECT */
  .glass {
    backdrop-filter: blur(14px);
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 0.75rem;
    box-shadow: 0 12px 28px rgba(0,0,0,0.45);
  }

  .skill-card {
    padding: 1.1rem 1.25rem;
  }

  .skill-title {
    font-size: 1rem;
    font-weight: 600;
    color: #55cc88; /* muted green */
    margin-bottom: 0.55rem;
  }

  /* GLASS BAR */
  .glass-bar {
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    height: 12px;
    overflow: hidden;
    margin-bottom: 0.45rem;
    backdrop-filter: blur(6px);
  }

  .skill-fill {
    height: 100%;
    background: linear-gradient(to right, #55cc88, #00aaff, #ff4444);
    border-radius: 999px;
    box-shadow: 0 0 12px rgba(85,204,136,0.4);
  }

  /* LEVEL WIDTHS */
  .level-1 { width: 20%; }
  .level-2 { width: 40%; }
  .level-3 { width: 60%; }
  .level-4 { width: 80%; }
  .level-5 { width: 100%; }

  .skill-level {
    font-size: 0.85rem;
    color: #9ca3af;
  }
</style>