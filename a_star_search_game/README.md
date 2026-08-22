# 🚗 A* City Navigator Game (AI Lab Project)

A visual simulation game built with **Python & Pygame** that demonstrates the **A\* (A-Star) Pathfinding Algorithm** in a dense urban city environment.

---

## 📂 Project Architecture

The project is modularized into two isolated layers:

```
a_star_search_game/
├── core_logic.py     # 🧠 Core A* Algorithm & Graph Representation (Pure Python, No Pygame)
├── graphics.py       # 🎨 Pygame Visualizer, UI Dashboard, Particles & Vehicle Animations
├── main.py           # 🚀 Game State Loop & Input Event Handler
└── README.md         # 📖 Project Documentation
```

### 1. `core_logic.py` (Core Algorithm)
- **Zero UI Dependency**: Can be imported and used anywhere independently.
- **Formula**:
  $$\mathbf{f(n) = g(n) + h(n)}$$
  - $g(n)$: Exact movement cost from start to node $n$ (Avenues = 1.0, Streets = 1.4, Alleys = 2.0).
  - $h(n)$: Heuristic estimate to the destination (supports Euclidean and Manhattan distance).
  - $f(n)$: Total estimated path cost.
- **Data Structures**: Priority Queue via Python's `heapq`, `came_from` dictionary for backwards path reconstruction, and visited sets for tracking explored nodes.

### 2. `graphics.py` (Visuals & Animation)
- **Urban Environment**: Renders road networks (avenues, streets), 3D isometric high-rise buildings with lighting, parks, and rooftop details.
- **Smooth Travel Animation**: Smooth sub-pixel vector interpolation of vehicle position along shortest path waypoints with realistic car orientation angle $\theta = \text{atan2}(\Delta y, \Delta x)$, dynamic headlights, and exhaust particles.
- **Telemetry HUD**: Displays current coordinates, explored node count, shortest path cost, journey progress bar, and controls.

### 3. `main.py` (Game Runner)
- Manages user interactions (point selection, speed adjustments, heuristic toggling).

---

## 🕹️ Controls & Hotkeys

| Action | Control |
|---|---|
| **Select Start / Goal Point** | `Left Click` on map |
| **Replay Travel Animation** | `[SPACE]` |
| **Change Travel Speed** | `[1]` (1x), `[2]` (2x), `[3]` (4x) |
| **Toggle Heuristic** | `[H]` (Euclidean $\leftrightarrow$ Manhattan) |
| **Generate New City** | `[G]` |
| **Reset Selection** | `[R]` |

---

## 🚀 How to Run

Navigate to the game directory and run:

```bash
cd a_star_search_game
python main.py
```
