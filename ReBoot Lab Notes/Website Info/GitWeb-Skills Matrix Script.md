<!-- SKILLS GRID SECTION -->
<section id="skills" class="fade-in">
  <h2>Skills Matrix</h2>

  <div class="skills-grid">

    <!-- Python -->
    <div class="skill-card">
      <div class="skill-title">Python</div>
      <div class="skill-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- JavaScript -->
    <div class="skill-card">
      <div class="skill-title">JavaScript</div>
      <div class="skill-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- C / C-Style -->
    <div class="skill-card">
      <div class="skill-title">C / C-Style Logic</div>
      <div class="skill-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- HTML -->
    <div class="skill-card">
      <div class="skill-title">HTML</div>
      <div class="skill-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- CSS -->
    <div class="skill-card">
      <div class="skill-title">CSS</div>
      <div class="skill-bar">
        <div class="skill-fill level-4"></div>
      </div>
      <div class="skill-level">Intermediate‑Plus</div>
    </div>

    <!-- Markdown -->
    <div class="skill-card">
      <div class="skill-title">Markdown</div>
      <div class="skill-bar">
        <div class="skill-fill level-3"></div>
      </div>
      <div class="skill-level">Intermediate</div>
    </div>

    <!-- Bash -->
    <div class="skill-card">
      <div class="skill-title">Bash / Shell</div>
      <div class="skill-bar">
        <div class="skill-fill level-2"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

    <!-- YAML -->
    <div class="skill-card">
      <div class="skill-title">YAML / Config</div>
      <div class="skill-bar">
        <div class="skill-fill level-1"></div>
      </div>
      <div class="skill-level">Beginner</div>
    </div>

  </div>
</section>

<!-- SKILLS GRID CSS -->
<style>
  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.2rem;
    margin-top: 1.2rem;
  }

  .skill-card {
    background: linear-gradient(135deg, rgba(10,0,20,0.9), rgba(5,0,10,0.95));
    border: 1px solid rgba(255,255,255,0.08);
    padding: 1rem 1.2rem;
    border-radius: 0.75rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.45);
  }

  .skill-title {
    font-size: 1rem;
    font-weight: 600;
    color: #55cc88; /* muted green */
    margin-bottom: 0.5rem;
  }

  .skill-bar {
    width: 100%;
    height: 10px;
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 0.4rem;
  }

  .skill-fill {
    height: 100%;
    background: linear-gradient(to right, #55cc88, #00aaff);
    border-radius: 999px;
  }

  /* Skill Levels (1–5) */
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
