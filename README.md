# LUCA: Genesis to Cosmos — 3D Evolution Game (`scorputer/3DGame`)

An epic, playable 3D Evolution Game inspired by *Spore* (2008), taking the player from the **Big Bang**, stellar nucleosynthesis, and **Hydrothermal Vent RNA Soup** all the way to multi-biome co-evolution, viral pandemics, and cosmic leviathans.

## Cross-Platform Stack Architecture (Windows, Android, iOS, Linux)

Rather than maintaining separate Java (Android) and Objective-C/Swift (iOS) rendering codebases, this project uses a **hybrid Python + Three.js WebGL/PWA architecture**:
1. **Python Core Simulation Engine (`src/luca_engine/`)**:
   - Strictly adheres to **PEP8** standards with comprehensive junior-developer docstrings and block comments.
   - Modular separation across `cosmos.py` (Big Bang & RNA Soup puzzle), `creature.py` (DNA traits, pinch/stretch morphology, stat computation), `world.py` (Micro-to-Macro biome physics, bump combat/feeding, cognitive button mechanisms, NPC co-evolution), and `logger.py` (structured audit logging).
2. **Universal 3D WebGL Client (`web_client/luca_3d_evolution.html`)**:
   - Runs natively at 60 FPS on **Windows, Android, iOS, and Linux** via hardware-accelerated WebGL (`Three.js`) with unified **Touch (pinch/stretch/tap)** and **Mouse/Keyboard** controls, plus procedural Web Audio API sound synthesis.
   - Can be packaged into native Android (`.apk`) and iOS (`.ipa`) binaries via Capacitor/Cordova or Android WebView wrapper, or hosted directly via the included **Docker container**.

## Repository Structure

```text
3DGame/
├── .github/workflows/regression.yml  # GitHub Actions CI: PEP8 lint + unit tests
├── Dockerfile                        # Containerized build with automated test gate
├── docker-compose.yml                # One-command container orchestration
├── server.py                         # Python HTTP + simulation bridge server
├── src/luca_engine/
│   ├── __init__.py
│   ├── logger.py                     # Centralized PEP8 audit & memory logger
│   ├── cosmos.py                     # Big Bang epochs & Hydrothermal RNA puzzle
│   ├── creature.py                   # Creature Creator, pinch/stretch morphs, stats
│   └── world.py                      # Biomes, physics, bump interactions, NPC AI
├── tests/
│   └── test_evolution_engine.py      # Full unittest regression suite
└── web_client/
    └── luca_3d_evolution.html        # Self-contained playable 3D WebGL game
```

## Quick Start

### 1. Run Unit & Regression Tests Locally
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### 2. Run in Docker
```bash
docker compose up --build
# Open http://localhost:8080 on Windows, Linux, Android, or iOS
```

### 3. Push to GitHub (`https://github.com/scorputer/3DGame`)
```bash
git init
git remote add origin https://github.com/scorputer/3DGame.git
git add .
git commit -m "feat: initial LUCA 3D evolution engine, WebGL client, and CI suite"
git branch -M main
git push -u origin main
```
