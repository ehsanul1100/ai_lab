# 🚗 A* City Navigator (Interactive AI Lab Project)

A visual simulation game built with **Python & Pygame** that demonstrates the **A\* (A-Star) Pathfinding Algorithm** across multiple procedural urban city environments.

---

## 🌟 Key Features

1. **Diverse Procedural City Presets (UI Clickable)**:
   - ✈️ **Airport Hub**: International terminal concourse, long tarmac runways with threshold dashes, taxiways, and airport loop expressways.
   - 🚦 **Busy Traffic Downtown**: Congested bottleneck streets (Cost $3.5$) surrounded by high-speed bypass ring expressways (Cost $1.0$). Demonstrates how A\* intelligently detours around heavy traffic!
   - 🏙️ **Metropolis**: High-density grid with diagonal expressways, boulevard avenues, and central plazas.
   - 🌊 **Coastal River**: Winding water canals, island districts, and bridges with custom crossing weights.
   - 🏰 **Old Town**: Organic winding cobblestone alleys, random-walk roads, and plazas.
   - ⚡ **Cyberpunk**: Super-block mega towers and interconnected alleyways.
   - 🎲 **Random Sprawl**: Pure procedural organic arterial urban sprawl.

2. **Lush Tree & Foliage System**:
   - Multi-shaded organic trees with shadows, trunks, and layered leafy canopies across parks, sidewalks, and nature buffer zones.

3. **Interactive UI Sidebar Dashboard**:
   - Direct on-screen clickable buttons for map presets, random generator, journey replay, speed ($1\times, 2\times, 4\times$), and heuristic toggling.
   - Live route telemetry showing $g(n)$, $h(n)$, and $f(n)$ calculations.

4. **Clean Startup**:
   - Starts with a clean map and no pre-selected points with an on-screen guidance banner.

5. **Realistic Driving Simulation**:
   - Car with smooth rotation $\theta = \text{atan2}(\Delta y, \Delta x)$, dynamic headlights beam, exhaust particles, and a glowing golden trail marking the traversed route.

---

## 📂 Project Architecture

```
a_star_search_game/
├── core_logic.py     # 🧠 Core A* Algorithm & Graph Map Generator (Pure Python, No Pygame)
├── graphics.py       # 🎨 Pygame Visualizer, UI Buttons, Airport, Trees & Car Animation
├── main.py           # 🚀 Main Game Loop & Click/Event Dispatcher
└── README.md         # 📖 Project Documentation
```

---

## 🕹️ Controls

- **`Left Click` (Map)**:
  - **1st Click**: Places the **Start Point** (Green Marker).
  - **2nd Click**: Places the **Destination** (Red Goal Beacon) $\rightarrow$ A\* finds the shortest path and the car drives.
- **`Left Click` (Sidebar UI Buttons)**:
  - Select any city preset (`Airport`, `Busy Traffic`, `Metropolis`, `Coastal`, `Old Town`, `Cyberpunk`, `Random Sprawl`), replay journey, adjust speed, or toggle heuristic.
- **Keyboard Shortcuts**:
  - `[SPACE]`: Replay Drive
  - `[1 / 2 / 3]`: Change Speed ($1\times, 2\times, 4\times$)
  - `[H]`: Toggle Heuristic (Euclidean $\leftrightarrow$ Manhattan)
  - `[G]`: Generate New City Layout
  - `[R]`: Reset Selection

---

## 🚀 How to Run

```powershell
cd e:\D_drive\Documents\ai_lab\a_star_search_game
python main.py
```
