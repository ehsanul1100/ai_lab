# 🚗 A* City Navigator (Interactive AI Lab Project)

A visual simulation game built with **Python & Pygame** that demonstrates the **A\* (A-Star) Pathfinding Algorithm** with step-by-step search wave traversal and driving animation across procedural urban city environments.

---

## 🌟 Interactive Animation Phases

When you pick a **Start** and **Destination** on the map, the simulation runs through 3 distinct visual phases:

1. 🔍 **Phase 1: Step-by-Step Node Traversal & Search Tree Exploration**:
   - The A\* search wave dynamically expands node-by-node in real time.
   - Connected **exploratory branches** ($came\_from$ parent-to-child tree lines) illustrate how the frontier propagates.
   - The **currently active evaluated node** features a pulsing golden radar scanner ring displaying live evaluation metrics.
   - Telemetry tracks evaluated node counts and $f(n) = g(n) + h(n)$ formulas live in the sidebar.

2. ⚡ **Phase 2: Shortest Path Discovery & Laser Lock**:
   - As soon as the search wave touches the destination, the optimal shortest path locks in with an electric neon cyan laser beam!

3. 🏎️ **Phase 3: Vehicle Driving Journey**:
   - The vehicle smoothly drives along the shortest path waypoints with dynamic headlights, smooth turn orientation, and a glowing golden traversed trail.

---

## 🏙️ City Presets & Features

- ✈️ **Airport Hub**: International terminal concourse, long tarmac runways with threshold dashes, taxiways, and airport loop expressways.
- 🚦 **Busy Traffic Downtown**: Congested bottleneck streets (Cost $3.5$) vs outer high-speed ring highways (Cost $1.0$). Demonstrates how A\* detours around traffic jams!
- 🏙️ **Metropolis**: High-density grid with diagonal expressways, boulevard avenues, and central plazas.
- 🌊 **Coastal River**: Winding water canals, island districts, and bridges with custom crossing weights.
- 🏰 **Old Town**: Organic winding cobblestone alleys, random-walk roads, and plazas.
- ⚡ **Cyberpunk**: Super-block mega towers and interconnected alleyways.
- 🎲 **Random Sprawl**: Pure procedural organic arterial urban sprawl.
- 🌳 **Lush Tree System**: Multi-shaded vector trees with drop shadows and leafy foliage.

---

## 🕹️ Full UI Buttons & Controls

- **`[🗑️ Reset & Restart Path (R)]`**: Instantly clears the Start & Destination points and resets the path anytime (useful if no path exists or to pick new points).
- **`[🔁 Replay (Space)]`**: Replays the entire sequence (Node Traversal $\rightarrow$ Path Discovery $\rightarrow$ Car Drive).
- **`[⏭️ Skip to Drive]`**: Skips the search traversal animation and jumps straight to driving.
- **`[1x | 2x | 4x Speed]`**: Adjusts animation speed for both node exploration and vehicle driving.
- **`[🧭 Heuristic Toggle (H)]`**: Toggles Euclidean $\leftrightarrow$ Manhattan distance.
- **`[🎲 Generate Random Sprawl]`**: Generates a brand new procedural city map.

---

## 🚀 How to Run

```powershell
cd e:\D_drive\Documents\ai_lab\a_star_search_game
python main.py
```
