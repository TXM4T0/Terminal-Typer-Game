# ⚡ TERMINAL TYPER: BATTLE PROTOCOL

<div align="center">

```
  _______ _____ _____  __  __ _____ _   _          _      
 |__   __|_   _|  __ \|  \/  |_   _| \ | |   /\   | |     
    | |    | | | |__) | \  / | | | |  \| |  /  \  | |    
    | |    | | |  ___/| |\/| | | | | . ` | / /\ \ | |     
    | |   _| |_| |    | |  | |_| |_| |\  |/ ____ \| |____ 
    |_|  |_____|_|    |_|  |_|_____|_| \_/_/    \_\______|
```

**A retro 8-bit turn-based cyberpunk terminal RPG powered by real-time keystroke telemetry.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(stdlib)-success.svg?style=for-the-badge)](https://docs.python.org/3/library/)
[![Tests](https://img.shields.io/badge/tests-38%2F38%20passing-brightgreen.svg?style=for-the-badge)](tests/)
[![Audio](https://img.shields.io/badge/audio-8--bit%20async%20WAV-orange.svg?style=for-the-badge)](terminaltyper/assets/sfx/)
[![Terminal](https://img.shields.io/badge/display-ANSI%2080--col-blueviolet.svg?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)

[Quick Start](#-quick-start) • [Gameplay Preview](#-gameplay-preview) • [Features](#-key-features) • [Combat Mechanics](#-combat-mechanics--telemetry) • [Boss Encounters](#-the-7-sector-bosses) • [Architecture](#-project-architecture) • [Tests](#-testing--verification)

</div>

---

## 📖 Overview

**Terminal Typer: Battle Protocol** blends the tactical turn-based combat of classic 8-bit monster battlers (*Pokémon*-style viewports) with high-intensity speed typing mechanics. 

Instead of passive dice rolls, **every action you execute is converted directly from your raw typing telemetry**:
* **Gross & Net WPM** determines your kinetic strike damage and HP restoration.
* **Character-level Accuracy** gates move success and triggers critical strikes.
* **Burst Timing & Cadence** enables split-second parries that deflect incoming boss attacks.

Built entirely on the **Python standard library** with **zero external dependencies** (`pip install` not required).

---

## 🎮 Gameplay Preview

The game renders within a strict, flicker-free **80-column ANSI viewport** split into three distinct tactical zones:

```text
+------------------------------------------------------------------------------+
| [VOID SOVEREIGN]                                 Lv. 20                      |
| HP: [██████████████░░░░░░] 380/550                                           |
| STATUS: [NORMAL]                                    .---.                    |
|                                                    /     \                   |
|                                                   (  o   o )                 |
|                                                    \  ___ /                  |
|                                                   _.'     '._                |
|                                                  (___________)               |
|   [OPERATOR] Lv. 20                                                          |
|   HP: [████████████████████] 100/100                                         |
|   STATUS: [NORMAL]                                                           |
+------------------------------------------------------------------------------+
| DIALOGUE: The anomaly pulses violently, fracturing the input matrix!         |
| PROMPT  : #h# abyss l##ks b#ck thr##gh br#k#n gl#ss.                         |
| INPUT   : The abyss looks back through broken glass._                        |
| TELEMETRY: 92.4 GROSS WPM | ACC: 100.0% | NET: 92.4 WPM [CRITICAL HIT!]      |
+------------------------------------------------------------------------------+
| [1] JAB        : Rapid strike (Low DMG, Short Word, 70% Acc Threshold)       |
| [2] HEAVY      : Devastating strike (High DMG, Complex Word, 80% Threshold)  |
| [3] PARRY      : Damage deflection shield (Up to 75% Mitigation, 90% Acc)    |
| [4] REST       : Nano-repair protocol (HP Recovery, 85% Acc Threshold)       |
+------------------------------------------------------------------------------+
```

---

## 🚀 Quick Start

### Prerequisites
* **Python 3.10+** (Standard library only — no `pip` or virtual environment required).
* **Terminal**: Windows Terminal, PowerShell, CMD, or any ANSI-compatible terminal (recommended size: `80 x 28` or larger).

### Installation & Launch

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/terminal-typer.git
   cd terminal-typer
   ```

2. **Launch immediately:**

   * **Using PowerShell (Recommended on Windows):**
     ```powershell
     ./run_game.ps1
     ```

   * **Using Windows Command Prompt (Batch):**
     ```cmd
     run_game.bat
     ```

   * **Using Python directly:**
     ```bash
     python main.py
     # or
     python -m terminaltyper
     ```

---

## ✨ Key Features

- **⚡ High-Precision Keystroke Telemetry Engine**
  Tracks typing duration with high-resolution monotonic timestamps (`time.perf_counter`), calculating character-level Levenshtein accuracy, Gross WPM, and Net WPM.
- **👶 Dedicated Baby Mode (Arrow-Only Attacks)**
  Novice & accessible game mode where attacks strictly consist of directional arrow sequences (`↑`, `↓`, `←`, `→`). Includes auto-spacing, generous timer windows (+50%), and 0.6x boss damage.
- **🎮 Universal Alternative Controls (WASD & Arrows)**
  Seamlessly execute directional moves with physical arrow keys OR `W`, `A`, `S`, `D` keys. Select battle actions via `[1-4]`, arrow directions (`↑` JAB, `→` HEAVY, `←` PARRY, `↓` REST), or WASD!
- **🔊 Asynchronous 8-Bit Retro Audio**
  15 custom 8-bit sound effects (WAV) played asynchronously via `winsound.PlaySound(..., SND_ASYNC)` with zero typing latency. Includes synthetic frequency fallback for non-audio environments.
- **💥 Kinetic Terminal Visual FX**
  Dynamic animations including strike flash banners, smooth 4–8 step animated HP drains with tick audio, randomized ASCII particle disintegrations for defeated bosses, and hyperspace sector warp transitions.
- **👾 7 Unique Sector Boss Encounters**
  Progressive difficulty curves moving from home-row fundamentals to rhythm consonants, strict speed gates ($\le 2.5\text{s}$), case inversion, syntax punctuation, hex memory dumps, and full compound prose (or escalating arrow choreographies in Baby Mode!).
- **🛡️ Tactical Debuff System**
  Face real-time battle anomalies like **GLITCH** (masks characters into visual noise), **CHILL** (cuts input timers by 30%), **BURN** (damage over time), and **STUMBLE** (forces emergency recovery).
- **📊 Diagnostic Typing Benchmark**
  Standalone typing calibration mode with instant analysis of WPM, raw accuracy, error count, and character timing.
- **⚙️ Pure Standard Library Architecture**
  Zero third-party package dependencies. Guaranteed clean installation and execution on any modern Python setup.

---

## 🧮 Combat Mechanics & Telemetry

### 1. Telemetry Formulas

$$\text{Elapsed Minutes} = \frac{\text{Elapsed Seconds}}{60.0}$$

$$\text{Gross WPM} = \frac{\text{Length of Typed String} / 5.0}{\text{Elapsed Minutes}}$$

$$\text{Matching Characters} = \sum_{i=0}^{\min(\text{len}(T), \text{len}(U)) - 1} [T[i] == U[i]]$$

$$\text{Accuracy} = \frac{\text{Matching Characters}}{\max(\text{len}(\text{Target } T), \text{len}(\text{Typed } U))}$$

$$\text{Net WPM} = \text{Gross WPM} \times \text{Accuracy}$$

### 2. Action Commands

| Action | Word Profile | Combat Formula | Success Threshold |
| :--- | :--- | :--- | :--- |
| **`[1] JAB`** | Short word (3–5 chars) | $\text{Damage} = \text{Net WPM} \times 1.0 \times \text{Crit}$ | $\text{Accuracy} \ge 70\%$ |
| **`[2] HEAVY`** | Complex word (9–14 chars) | $\text{Damage} = \text{Net WPM} \times 2.2 \times \text{Crit}$ | $\text{Accuracy} \ge 80\%$ |
| **`[3] PARRY`** | Rhythm word (6–8 chars) | $\text{Mitigation \%} = \min(75\%, \text{Net WPM} \times 0.75\%)$ | $\text{Accuracy} \ge 90\%$ |
| **`[4] REST`** | 2–3 rhythmic words | $\text{HP Recovered} = \text{Net WPM} \times 0.60$ | $\text{Accuracy} \ge 85\%$ |

* **Critical Strike Trigger:** Achieved when $\text{Accuracy} = 100\%$ **AND** $\text{Net WPM} \ge 70.0$, applying a **$1.5\times$ damage multiplier**.
* **Action Fumble:** If accuracy falls below the required threshold, the action fails and deals $0$ damage.

### 3. Boss Turn & Mitigation

* Bosses select actions via weighted probability distributions.
* Boss base damage is rolled uniformly within their move's `[min_dmg, max_dmg]` range with a 10% chance for a boss critical strike ($1.35\times$).
* If the player executed a successful **PARRY**, incoming boss damage is mitigated:
$$\text{Damage Taken} = \max(1, \operatorname{Round}(\text{Boss Damage} \times (1.0 - \text{Mitigation \%})))$$

---

## 👾 The 7 Sector Bosses

| Sector | Boss | Level | Max HP | Challenge Focus & Typographic Domain | Status Effect |
| :---: | :--- | :---: | :---: | :--- | :---: |
| **1** | **Slime Core** | Lv. 3 | 120 | Home-row foundation (`glad`, `half`, `fall`, `dash`) | None |
| **2** | **Iron Golem** | Lv. 6 | 220 | Double consonants and steady rhythm cadence | **STUMBLE** |
| **3** | **Swift Falcon** | Lv. 8 | 180 | Rapid burst typing with strict time limit ($\le 2.5\text{s}$) | None |
| **4** | **Shadow Doppelgänger** | Lv. 11 | 260 | Alternating shift-key discipline (`DeFeAt`, `mIrRoR`) | **GLITCH** |
| **5** | **Frost Lich** | Lv. 15 | 320 | Punctuation, dashes, and contractions (`ice-cold`, `it's`) | **CHILL** |
| **6** | **Cyber Mech** | Lv. 18 | 400 | Hexadecimal addresses, code syntax, and symbols | **BURN** |
| **7** | **Void Sovereign** | Lv. 20 | 550 | Full multi-word compound prose under pressure | Random |

---

## ☣️ Status Effects & Debuffs

* 🧩 **GLITCH (Shadow Doppelgänger / Void Sovereign)**
  Masks 25% of prompt letters into terminal static (`#`, `@`, `%`, `*`). The player must deduce the missing letters from contextual memory and type the uncorrupted string. *(Duration: 2 turns)*
* ❄️ **CHILL (Frost Lich / Void Sovereign)**
  Freezes keyboard input buffers: cuts the countdown timer before automatic fumble by **30%**. *(Duration: 2 turns)*
* 🔥 **BURN (Cyber Mech / Void Sovereign)**
  Overheats terminal circuitry: inflicts **10 unblockable true damage** at the end of each turn. *(Duration: 3 turns)*
* 💫 **STUMBLE (Iron Golem)**
  Concussive disorientation: locks the command palette on the subsequent turn and forces an immediate emergency recovery prompt. *(Duration: 1 turn)*

---

## 📁 Project Architecture

```
terminal-typer/
├── terminaltyper/
│   ├── assets/
│   │   └── sfx/                 # 15 authentic 8-bit retro sound effect WAVs
│   ├── core/
│   │   ├── metrics.py           # High-resolution telemetry & WPM math engine
│   │   ├── models.py            # Player, Boss, Move, Action, Status dataclasses
│   │   ├── sound.py             # Asynchronous WAV sound engine & synthetic fallback
│   │   └── terminal.py          # Cross-platform raw input & terminal mode handler
│   ├── data/
│   │   ├── bosses.json          # Master manifest for 7 bosses, moves & word banks
│   │   └── loader.py            # Prompt selector, bank loader, and glitch masker
│   ├── game/
│   │   ├── battle.py            # Active battle session, real-time typing loop & VFX
│   │   ├── engine.py            # Campaign state machine & sector transitions
│   │   ├── settings.py          # Interactive settings menu & configuration
│   │   └── typing_test.py       # Standalone diagnostic typing benchmark
│   └── ui/
│       ├── animations.py        # BIOS POST sequence, warp drive, particle dissolve FX
│       ├── ansi.py              # ANSI color definitions, string math & HP bars
│       └── renderer.py          # Fixed 80-column 3-zone arena layout engine
├── tests/
│   ├── test_bosses.py           # Boss data integrity & word bank tests
│   ├── test_combat.py           # Damage, parry formulas, and status effect tests
│   ├── test_difficulty_and_controls.py # Baby Mode, arrow-only attacks, WASD & difficulty tests
│   ├── test_metrics.py          # WPM, accuracy, and critical strike tests
│   ├── test_renderer.py         # Strict 80-column layout & viewport sizing tests
│   ├── test_simulation.py       # End-to-end headless battle & campaign tests
│   └── test_sound_and_animations.py # Audio playback & visual animation unit tests
├── main.py                      # Root launcher script
├── run_game.bat                 # Windows Batch one-click launcher
├── run_game.ps1                 # Windows PowerShell one-click launcher
└── README.md                    # Technical documentation & repository overview
```

---

## ⚙️ Settings & Customization

Access the **Settings Menu** directly from the main title screen:

```text
+------------------------------------------------------------------------------+
| [TERMINAL PROTOCOL SETTINGS & SYSTEM CONFIG]                                |
+------------------------------------------------------------------------------+
   [1] Difficulty Mode         : BABY (Novice / Arrow-Only)
   [2] Alternative Controls   : ARROWS + WASD (Universal)
   [3] Audio / 8-Bit SFX       : ENABLED
   [4] Narrative Text Speed    : RETRO (Normal)
   [5] Combat Timer Scaling    : STANDARD (Normal)
   [6] Screen Flash / Impact   : ENABLED
   [7] Combat & VFX Animations : ENABLED
   [R] Reset to Default Settings
   [0] Save & Return to Main Menu
```

* **Difficulty Mode**:
  * `BABY (Novice)`: Attacks only consist of arrow keys (`↑`, `↓`, `←`, `→`). +50% time limit, 0.6x boss damage, and relaxed crits.
  * `NORMAL (Standard)`: Full tactical typing protocol with themed vocabulary, symbols, and prose.
  * `HARD (Cyber Overclock)`: 1.25x boss damage, -25% timer window, and tighter accuracy thresholds (+5%).
* **Alternative Controls**:
  * `ARROWS + WASD (Universal)`: Use either physical arrow keys OR `W`, `A`, `S`, `D` interchangeably.
  * `ARROW KEYS ONLY`: Physical arrow keys only.
  * `WASD KEYS ONLY`: `W` (Up), `S` (Down), `A` (Left), `D` (Right).
* **Audio / 8-Bit SFX**: Toggle asynchronous 8-bit sound effects.
* **Narrative Text Speed**: Configure typewriter delay between `FAST (5ms)`, `NORMAL (15ms)`, and `INSTANT (0ms)`.
* **Combat & VFX Animations**: Enable or disable dynamic HP drain frames, strike banners, and ASCII disintegrations.
* **Combat Timer Scaling**: Fine-tune timer windows (`STANDARD`, `RELAXED`, `HARDCORE`).

---

## 🧪 Testing & Verification

The project includes a comprehensive automated test suite with **38 unit tests** validating mathematical accuracy, combat mechanics, and viewport formatting:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Coverage Highlights
* **Difficulty & Controls (`test_difficulty_and_controls.py`)**: Tests Baby Mode arrow-only attacks for all 7 bosses, WASD/arrow key normalization, accuracy offsets, and 80-column palette alignment.
* **Telemetry & Formulas (`test_metrics.py`)**: Validates Gross WPM, character-level matching, unequal string lengths, and critical hit thresholds.
* **Combat Engine (`test_combat.py`)**: Tests parry mitigation curves, rest healing, burn damage over time, and chill timer reductions.
* **Boss Manifest (`test_bosses.py`)**: Ensures all 7 bosses adhere to schema, level progression, and required word banks.
* **Layout Renderer (`test_renderer.py`)**: Validates that all frames strictly maintain 80 visible columns without ANSI overflow or terminal distortion.
* **Audio & Visuals (`test_sound_and_animations.py`)**: Verifies WAV file headers, non-blocking playback interfaces, warp animation loops, and ASCII dissolve particle generators.

---

## 🛠️ Modding & Custom Bosses

Adding custom bosses is as simple as adding a new JSON object to [`terminaltyper/data/bosses.json`](terminaltyper/data/bosses.json):

```json
{
  "id": "boss_custom",
  "name": "Quantum Spectre",
  "level": 25,
  "max_hp": 650,
  "theme": "Complex scientific terminology and regex patterns",
  "ascii": [
    "      .---.       ",
    "     / * * \\      ",
    "    |   ^   |     ",
    "     \\ 'v' /      ",
    "      '---'       "
  ],
  "moves": [
    { "name": "Superposition Strike", "min_dmg": 22, "max_dmg": 30, "weight": 60, "status": "GLITCH" },
    { "name": "Wave Collapse", "min_dmg": 35, "max_dmg": 45, "weight": 40, "status": "BURN" }
  ],
  "word_banks": {
    "jab": ["quark", "boson", "hadron", "gluon"],
    "heavy": ["superposition", "entanglement", "interferometer"],
    "parry": ["decohere", "wavefunction", "uncertainty"],
    "rest": ["ground state", "zero energy", "thermal bath"]
  }
}
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
  <sub>Engineered with precision for the terminal enthusiast. Type fast. Strike true.</sub>
</div>
