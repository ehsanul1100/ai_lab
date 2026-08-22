"""
=============================================================================
A* SEARCH ALGORITHM & CITY GRAPH ENGINE (CORE LOGIC)
=============================================================================
Isolated Core AI Engine:
  1. Procedural City Map Generator with Rich Urban Presets:
     - ✈️ Airport Hub City (Terminal, Runway, Taxiways, Access Expressways)
     - 🚦 Rush Hour Downtown (Busy Congested Streets vs Fast Ring Bypass)
     - 🏙️ Metropolis Boulevard (Tree-lined Avenues & Central Plaza)
     - 🌊 Coastal River (Bridges & Waterfront Promenades)
     - 🏰 Old Town Maze (Organic Winding Roads & Courtyards)
     - ⚡ Cyberpunk Mega-District
     - 🎲 Procedural Random Urban Sprawl
  2. Diverse Road Types with Differential Movement Costs (Avenues, Busy Traffic, Runways, Bridges)
  3. Building Architecture Shapes & Tree Foliage Placement Map
  4. Manhattan & Euclidean Heuristic Functions
  5. Classic A* Search: f(n) = g(n) + h(n) with Path Reconstruction
=============================================================================
"""

import heapq
import math
import random
from typing import Dict, List, Tuple, Optional, Set

# Node representation: (col, row) coordinate on grid
Node = Tuple[int, int]

# Tile Type Constants
TILE_ROAD_AVENUE      = 0   # Fast expressway / avenue (Cost = 1.0)
TILE_ROAD_STREET      = 1   # Regular street (Cost = 1.5)
TILE_ROAD_ALLEY       = 2   # Narrow shortcut (Cost = 2.2)
TILE_ROAD_BRIDGE      = 3   # Bridge over water (Cost = 1.2)
TILE_ROAD_BUSY        = 4   # Heavy traffic congested street (Cost = 3.5)
TILE_RUNWAY           = 5   # Airport runway & taxiway (Cost = 1.0)
TILE_ROADBLOCK        = 6   # Construction / Impasse (Unpassable)
TILE_BUILDING         = 7   # Skyscraper / City Block (Impasse)
TILE_PARK             = 8   # Park & Green Lawn (Impasse)
TILE_WATER            = 9   # River / Ocean Bay (Impasse)
TILE_AIRPORT_TERMINAL = 10  # Airport Terminal Building (Impasse)

# Movement Cost mapping for traversable road tiles
ROAD_COSTS = {
    TILE_ROAD_AVENUE: 1.0,
    TILE_RUNWAY:      1.0,
    TILE_ROAD_BRIDGE: 1.2,
    TILE_ROAD_STREET: 1.5,
    TILE_ROAD_ALLEY:  2.2,
    TILE_ROAD_BUSY:   3.5,  # Congested traffic zone
}

# City Style Presets
STYLE_AIRPORT     = "Airport Hub"
STYLE_BUSY_STREET = "Busy Traffic"
STYLE_METROPOLIS  = "Metropolis"
STYLE_COASTAL     = "Coastal River"
STYLE_OLD_TOWN    = "Old Town Maze"
STYLE_CYBERPUNK   = "Cyberpunk Grid"
STYLE_RANDOM      = "Random Sprawl"

CITY_STYLES = [
    STYLE_AIRPORT, STYLE_BUSY_STREET, STYLE_METROPOLIS,
    STYLE_COASTAL, STYLE_OLD_TOWN, STYLE_CYBERPUNK, STYLE_RANDOM
]


# ==========================================
# 1. HEURISTIC FUNCTIONS
# ==========================================

def heuristic_euclidean(a: Node, b: Node) -> float:
    """Straight-line Euclidean distance."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def heuristic_manhattan(a: Node, b: Node) -> float:
    """Grid Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ==========================================
# 2. PROCEDURAL CITY MAP GENERATOR
# ==========================================

class CityMap:
    """
    Represents a dynamic urban network with multiple procedural layouts,
    airports, traffic congestion, bridges, water canals, trees, and buildings.
    """
    def __init__(self, cols: int = 28, rows: int = 20, style: str = STYLE_AIRPORT, seed: Optional[int] = None):
        self.cols = cols
        self.rows = rows
        self.style = style
        if seed is not None:
            random.seed(seed)
            
        self.grid: List[List[int]] = [[TILE_BUILDING for _ in range(rows)] for _ in range(cols)]
        self.building_heights: Dict[Node, int] = {}
        self.building_types: Dict[Node, int] = {}  # 0=standard, 1=helipad, 2=glass tower, 3=residential
        self.trees: Set[Tuple[float, float, int]] = set() # (x, y, tree_variant)
        self.road_nodes: List[Node] = []
        
        self.generate_city(self.style)

    def generate_city(self, style: str):
        """Dispatches to specific procedural city layout generators."""
        self.style = style
        self.trees.clear()

        # Reset base to buildings
        for c in range(self.cols):
            for r in range(self.rows):
                self.grid[c][r] = TILE_BUILDING
                self.building_heights[(c, r)] = random.randint(1, 4)
                self.building_types[(c, r)] = random.choice([0, 0, 1, 2, 3])

        if style == STYLE_AIRPORT:
            self._gen_airport()
        elif style == STYLE_BUSY_STREET:
            self._gen_busy_streets()
        elif style == STYLE_METROPOLIS:
            self._gen_metropolis()
        elif style == STYLE_COASTAL:
            self._gen_coastal()
        elif style == STYLE_OLD_TOWN:
            self._gen_old_town()
        elif style == STYLE_CYBERPUNK:
            self._gen_cyberpunk()
        else:
            self._gen_random_sprawl()

        self._populate_trees()
        self._update_road_nodes()

    def _update_road_nodes(self):
        self.road_nodes = [
            (c, r) for c in range(self.cols) for r in range(self.rows) 
            if self.is_road(c, r)
        ]

    # --- Generator 1: Airport Hub City ---
    def _gen_airport(self):
        split_c = self.cols // 2 - 1

        # Airport Runways
        runway_r1 = 4
        runway_r2 = 14
        for c in range(split_c + 3, self.cols - 1):
            self.grid[c][runway_r1] = TILE_RUNWAY
            self.grid[c][runway_r2] = TILE_RUNWAY

        # Taxiways
        for r in range(runway_r1, runway_r2 + 1):
            self.grid[split_c + 3][r] = TILE_RUNWAY
            self.grid[self.cols - 2][r] = TILE_RUNWAY

        # Terminal & Concourse
        for c in range(split_c + 1, split_c + 3):
            for r in range(7, 12):
                self.grid[c][r] = TILE_AIRPORT_TERMINAL

        # Airport Green Grass Zone
        for c in range(split_c + 4, self.cols - 2):
            for r in range(runway_r1 + 2, runway_r2 - 1):
                self.grid[c][r] = TILE_PARK

        # Highway Loop
        for r in range(self.rows):
            self.grid[split_c][r] = TILE_ROAD_AVENUE
        for c in range(split_c, self.cols):
            self.grid[c][1] = TILE_ROAD_AVENUE
            self.grid[c][self.rows - 2] = TILE_ROAD_AVENUE

        # City Side (West)
        for c in range(1, split_c, 3):
            for r in range(self.rows):
                self.grid[c][r] = TILE_ROAD_AVENUE
        for r in range(2, self.rows - 2, 3):
            for c in range(split_c + 1):
                self.grid[c][r] = TILE_ROAD_STREET

    # --- Generator 2: Busy Traffic Downtown ---
    def _gen_busy_streets(self):
        # Ring expressway (Cost 1.0)
        for c in range(1, self.cols - 1):
            self.grid[c][1] = TILE_ROAD_AVENUE
            self.grid[c][self.rows - 2] = TILE_ROAD_AVENUE
        for r in range(1, self.rows - 1):
            self.grid[1][r] = TILE_ROAD_AVENUE
            self.grid[self.cols - 2][r] = TILE_ROAD_AVENUE

        # Congested downtown grid (Cost 3.5)
        for c in range(3, self.cols - 3, 2):
            for r in range(3, self.rows - 3):
                self.grid[c][r] = TILE_ROAD_BUSY if random.random() < 0.75 else TILE_ROAD_STREET

        for r in range(3, self.rows - 3, 2):
            for c in range(3, self.cols - 3):
                self.grid[c][r] = TILE_ROAD_BUSY if random.random() < 0.75 else TILE_ROAD_STREET

        mid_c = self.cols // 2
        for r in range(self.rows):
            self.grid[mid_c][r] = TILE_ROAD_AVENUE

        cx, cy = self.cols // 2, self.rows // 2
        for dc in (-2, -1, 1, 2):
            for dr in (-1, 0, 1):
                if 0 <= cx + dc < self.cols and 0 <= cy + dr < self.rows:
                    if self.grid[cx + dc][cy + dr] == TILE_BUILDING:
                        self.grid[cx + dc][cy + dr] = TILE_PARK

    # --- Generator 3: Metropolis Grid with Boulevards ---
    def _gen_metropolis(self):
        for c in range(self.cols):
            if c % 5 == 2 or c == 1 or c == self.cols - 2:
                for r in range(self.rows):
                    self.grid[c][r] = TILE_ROAD_AVENUE

        for r in range(self.rows):
            if r % 4 == 1 or r == 1 or r == self.rows - 2:
                for c in range(self.cols):
                    self.grid[c][r] = TILE_ROAD_AVENUE

        for c in range(1, self.cols - 1, 2):
            for r in range(1, self.rows - 1):
                if self.grid[c][r] == TILE_BUILDING and random.random() < 0.75:
                    self.grid[c][r] = TILE_ROAD_STREET

        for r in range(1, self.rows - 1, 2):
            for c in range(1, self.cols - 1):
                if self.grid[c][r] == TILE_BUILDING and random.random() < 0.75:
                    self.grid[c][r] = TILE_ROAD_STREET

        for i in range(min(self.cols, self.rows)):
            if 0 <= i < self.cols and 0 <= i < self.rows:
                self.grid[i][i] = TILE_ROAD_AVENUE

        cx, cy = self.cols // 2, self.rows // 2
        for dc in (-2, -1, 0, 1):
            for dr in (-1, 0, 1):
                px, py = cx + dc, cy + dr
                if 0 <= px < self.cols and 0 <= py < self.rows:
                    if self.grid[px][py] == TILE_BUILDING:
                        self.grid[px][py] = TILE_PARK

    # --- Generator 4: Coastal River Islands with Bridges ---
    def _gen_coastal(self):
        river_c = self.cols // 2
        river_tiles = set()
        for r in range(self.rows):
            offset = int(math.sin(r * 0.4) * 3)
            rc = max(4, min(self.cols - 5, river_c + offset))
            for w in (-1, 0, 1):
                if 0 <= rc + w < self.cols:
                    self.grid[rc + w][r] = TILE_WATER
                    river_tiles.add((rc + w, r))

        for c in range(1, river_c - 2, 3):
            for r in range(self.rows):
                self.grid[c][r] = TILE_ROAD_STREET
        for r in range(1, self.rows - 1, 3):
            for c in range(1, river_c - 1):
                if (c, r) not in river_tiles:
                    self.grid[c][r] = TILE_ROAD_AVENUE

        for c in range(river_c + 3, self.cols - 1, 3):
            for r in range(self.rows):
                self.grid[c][r] = TILE_ROAD_STREET
        for r in range(1, self.rows - 1, 3):
            for c in range(river_c + 2, self.cols - 1):
                if (c, r) not in river_tiles:
                    self.grid[c][r] = TILE_ROAD_AVENUE

        for r in range(self.rows):
            offset = int(math.sin(r * 0.4) * 3)
            rc = max(4, min(self.cols - 5, river_c + offset))
            if rc - 2 >= 0 and self.grid[rc - 2][r] != TILE_WATER:
                self.grid[rc - 2][r] = TILE_ROAD_AVENUE
            if rc + 2 < self.cols and self.grid[rc + 2][r] != TILE_WATER:
                self.grid[rc + 2][r] = TILE_ROAD_AVENUE

        bridge_rows = [3, self.rows // 2, self.rows - 4]
        for br in bridge_rows:
            for c in range(self.cols):
                if self.grid[c][br] == TILE_WATER:
                    self.grid[c][br] = TILE_ROAD_BRIDGE
                elif self.grid[c][br] == TILE_BUILDING:
                    self.grid[c][br] = TILE_ROAD_AVENUE

    # --- Generator 5: European Old Town ---
    def _gen_old_town(self):
        for _ in range(14):
            c = random.randint(2, self.cols - 3)
            r = random.randint(2, self.rows - 3)
            length = random.randint(25, 45)
            dc, dr = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

            for _ in range(length):
                if 1 <= c < self.cols - 1 and 1 <= r < self.rows - 1:
                    road_type = TILE_ROAD_STREET if random.random() < 0.7 else TILE_ROAD_ALLEY
                    self.grid[c][r] = road_type
                    if random.random() < 0.25:
                        dc, dr = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    c += dc
                    r += dr

        for c in range(1, self.cols - 1):
            self.grid[c][1] = TILE_ROAD_AVENUE
            self.grid[c][self.rows - 2] = TILE_ROAD_AVENUE
        for r in range(1, self.rows - 1):
            self.grid[1][r] = TILE_ROAD_AVENUE
            self.grid[self.cols - 2][r] = TILE_ROAD_AVENUE

        cx, cy = self.cols // 2, self.rows // 2
        for dc in range(-2, 3):
            for dr in range(-2, 3):
                self.grid[cx + dc][cy + dr] = TILE_ROAD_STREET

    # --- Generator 6: Cyberpunk Dense Mega-District ---
    def _gen_cyberpunk(self):
        for c in range(self.cols):
            if c % 3 == 0:
                for r in range(self.rows):
                    self.grid[c][r] = TILE_ROAD_AVENUE
        for r in range(self.rows):
            if r % 3 == 0:
                for c in range(self.cols):
                    self.grid[c][r] = TILE_ROAD_AVENUE

        for c in range(1, self.cols - 1):
            for r in range(1, self.rows - 1):
                if self.grid[c][r] == TILE_BUILDING:
                    self.building_heights[(c, r)] = random.randint(3, 4)
                    if random.random() < 0.35:
                        self.grid[c][r] = TILE_ROAD_ALLEY

    # --- Generator 7: Random Organic Sprawl ---
    def _gen_random_sprawl(self):
        mid_c = random.randint(self.cols // 3, 2 * self.cols // 3)
        mid_r = random.randint(self.rows // 3, 2 * self.rows // 3)
        for r in range(self.rows):
            self.grid[mid_c][r] = TILE_ROAD_AVENUE
        for c in range(self.cols):
            self.grid[c][mid_r] = TILE_ROAD_AVENUE

        for _ in range(30):
            start_c = random.choice([mid_c, random.randint(2, self.cols - 3)])
            start_r = random.choice([mid_r, random.randint(2, self.rows - 3)])
            orient = random.choice(["H", "V"])
            length = random.randint(4, 14)

            if orient == "H":
                r = start_r
                for dc in range(-length // 2, length // 2):
                    c = start_c + dc
                    if 0 <= c < self.cols:
                        self.grid[c][r] = TILE_ROAD_STREET
            else:
                c = start_c
                for dr in range(-length // 2, length // 2):
                    r = start_r + dr
                    if 0 <= r < self.rows:
                        self.grid[c][r] = TILE_ROAD_STREET

        for c in range(2, self.cols - 2):
            self.grid[c][2] = TILE_ROAD_AVENUE
            self.grid[c][self.rows - 3] = TILE_ROAD_AVENUE
        for r in range(2, self.rows - 2):
            self.grid[2][r] = TILE_ROAD_AVENUE
            self.grid[self.cols - 3][r] = TILE_ROAD_AVENUE

    # --- Tree & Foliage Population ---
    def _populate_trees(self):
        for c in range(self.cols):
            for r in range(self.rows):
                tile = self.grid[c][r]
                if tile == TILE_PARK:
                    num_trees = random.randint(2, 4)
                    for _ in range(num_trees):
                        ox = c + random.uniform(0.18, 0.82)
                        oy = r + random.uniform(0.18, 0.82)
                        self.trees.add((ox, oy, random.choice([0, 1, 2])))
                
                elif tile == TILE_ROAD_AVENUE and random.random() < 0.25:
                    for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        nc, nr = c + dc, r + dr
                        if 0 <= nc < self.cols and 0 <= nr < self.rows:
                            if self.grid[nc][nr] == TILE_BUILDING and random.random() < 0.20:
                                self.trees.add((nc + 0.5, nr + 0.5, random.choice([0, 1])))

    # --- Utility Methods ---
    def is_road(self, c: int, r: int) -> bool:
        """Returns True if the grid coordinate is a traversable road/runway."""
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.grid[c][r] in ROAD_COSTS
        return False

    def get_neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """Returns adjacent reachable road tiles and edge movement cost."""
        c, r = node
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for dc, dr in directions:
            nc, nr = c + dc, r + dr
            if self.is_road(nc, nr):
                road_type = self.grid[nc][nr]
                cost = ROAD_COSTS.get(road_type, 1.0)
                neighbors.append(((nc, nr), cost))

        return neighbors

    def get_nearest_road(self, col: int, row: int) -> Optional[Node]:
        """Finds the closest drivable road node to any clicked tile."""
        if self.is_road(col, row):
            return (col, row)
        
        best_node = None
        best_dist = float('inf')
        for rc, rr in self.road_nodes:
            d = (rc - col) ** 2 + (rr - row) ** 2
            if d < best_dist:
                best_dist = d
                best_node = (rc, rr)
        return best_node


# ==========================================
# 3. CORE A* SEARCH ALGORITHM
# ==========================================

class AStarResult:
    """Encapsulates the result and evaluation stats of an A* run."""
    def __init__(
        self, 
        path: List[Node], 
        total_cost: float, 
        visited_order: List[Node], 
        explored_count: int, 
        g_scores: Dict[Node, float],
        f_scores: Dict[Node, float]
    ):
        self.path = path
        self.total_cost = total_cost
        self.visited_order = visited_order
        self.explored_count = explored_count
        self.g_scores = g_scores
        self.f_scores = f_scores


def a_star_search(
    city_map: CityMap, 
    start: Node, 
    goal: Node, 
    heuristic_type: str = "euclidean"
) -> Optional[AStarResult]:
    """
    Classic A* Shortest Path Search on the City Graph.
    Formula: f(n) = g(n) + h(n)
    """
    if start == goal:
        return AStarResult([start], 0.0, [start], 1, {start: 0.0}, {start: 0.0})

    h_func = heuristic_euclidean if heuristic_type == "euclidean" else heuristic_manhattan

    counter = 0
    open_heap = []
    
    g_score: Dict[Node, float] = {start: 0.0}
    f_start = h_func(start, goal)
    f_score: Dict[Node, float] = {start: f_start}

    heapq.heappush(open_heap, (f_start, counter, start))
    
    came_from: Dict[Node, Node] = {}
    visited_set: Set[Node] = set()
    visited_order: List[Node] = []

    while open_heap:
        current_f, _, current = heapq.heappop(open_heap)

        if current in visited_set:
            continue

        visited_set.add(current)
        visited_order.append(current)

        if current == goal:
            path = []
            curr = goal
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            
            return AStarResult(
                path=path,
                total_cost=g_score[goal],
                visited_order=visited_order,
                explored_count=len(visited_set),
                g_scores=g_score,
                f_scores=f_score
            )

        for neighbor, edge_cost in city_map.get_neighbors(current):
            tentative_g = g_score[current] + edge_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h_val = h_func(neighbor, goal)
                f_val = tentative_g + h_val
                f_score[neighbor] = f_val

                counter += 1
                heapq.heappush(open_heap, (f_val, counter, neighbor))

    return None
