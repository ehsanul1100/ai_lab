"""
=============================================================================
A* SEARCH ALGORITHM & CITY GRAPH ENGINE (CORE LOGIC)
=============================================================================
This module is strictly isolated from Pygame/Graphics.
It contains:
  1. CityGrid / Graph Representation (Roads, Buildings, Intersections, Costs)
  2. Heuristic Functions (Manhattan, Euclidean)
  3. The Core A* (A-Star) Pathfinding Algorithm: f(n) = g(n) + h(n)
  4. Path Reconstruction and Exploration History for Visualizers
=============================================================================
"""

import heapq
import math
import random
from typing import Dict, List, Tuple, Optional, Set

# Node representation: (col, row) coordinate on grid
Node = Tuple[int, int]


# ==========================================
# 1. HEURISTIC FUNCTIONS
# ==========================================

def heuristic_euclidean(a: Node, b: Node) -> float:
    """Straight-line distance (Euclidean)."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def heuristic_manhattan(a: Node, b: Node) -> float:
    """Grid Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ==========================================
# 2. CITY MAP & GRAPH REPRESENTATION
# ==========================================

# Tile Type Constants
TILE_ROAD_AVENUE = 0   # Fast highway/avenue (Cost = 1.0)
TILE_ROAD_STREET = 1   # Regular street (Cost = 1.4)
TILE_ROAD_ALLEY  = 2   # Narrow alleyway (Cost = 2.0)
TILE_BUILDING    = 3   # Obstacle (Impasse)
TILE_PARK        = 4   # Park / Green space (Impasse)
TILE_WATER       = 5   # River / Water canal (Impasse)

# Movement Cost mapping for traversable tiles
ROAD_COSTS = {
    TILE_ROAD_AVENUE: 1.0,
    TILE_ROAD_STREET: 1.4,
    TILE_ROAD_ALLEY:  2.0,
}


class CityMap:
    """
    Represents a dense city with road networks, city blocks,
    high-rise buildings, parks, and bridges.
    """
    def __init__(self, cols: int = 28, rows: int = 20, seed: Optional[int] = None):
        self.cols = cols
        self.rows = rows
        if seed is not None:
            random.seed(seed)
            
        self.grid: List[List[int]] = [[TILE_BUILDING for _ in range(rows)] for _ in range(cols)]
        self.building_heights: Dict[Node, int] = {}
        self.building_colors: Dict[Node, int] = {}
        self.road_nodes: List[Node] = []
        
        self.generate_dense_city()

    def generate_dense_city(self):
        """Generates an intricate, dense urban grid with avenues, streets, and blocks."""
        # 1. Fill base with buildings
        for c in range(self.cols):
            for r in range(self.rows):
                self.grid[c][r] = TILE_BUILDING
                self.building_heights[(c, r)] = random.randint(1, 4)
                self.building_colors[(c, r)] = random.randint(0, 3)

        # 2. Carve Major Avenues (Broad arteries every 4-5 blocks)
        avenue_cols = [c for c in range(1, self.cols - 1) if c % 5 == 1]
        avenue_rows = [r for r in range(1, self.rows - 1) if r % 4 == 1]

        for c in avenue_cols:
            for r in range(self.rows):
                self.grid[c][r] = TILE_ROAD_AVENUE

        for r in avenue_rows:
            for c in range(self.cols):
                self.grid[c][r] = TILE_ROAD_AVENUE

        # 3. Carve Secondary Regular Streets
        for c in range(2, self.cols - 2, 2):
            for r in range(self.rows):
                if self.grid[c][r] == TILE_BUILDING and random.random() < 0.85:
                    self.grid[c][r] = TILE_ROAD_STREET

        for r in range(2, self.rows - 2, 2):
            for c in range(self.cols):
                if self.grid[c][r] == TILE_BUILDING and random.random() < 0.85:
                    self.grid[c][r] = TILE_ROAD_STREET

        # 4. Add Alleys / Shortcuts between blocks
        for _ in range(int(self.cols * self.rows * 0.1)):
            rc = random.randint(1, self.cols - 2)
            rr = random.randint(1, self.rows - 2)
            if self.grid[rc][rr] == TILE_BUILDING:
                # Only if connected to some road
                if any(self.is_road(nc, nr) for nc, nr in [(rc+1, rr), (rc-1, rr), (rc, rr+1), (rc, rr-1)]):
                    self.grid[rc][rr] = TILE_ROAD_ALLEY

        # 5. Place Central City Park / Plaza
        park_w = max(2, self.cols // 7)
        park_h = max(2, self.rows // 6)
        start_px = self.cols // 2 - park_w // 2
        start_py = self.rows // 2 - park_h // 2
        for c in range(start_px, start_px + park_w):
            for r in range(start_py, start_py + park_h):
                if 0 <= c < self.cols and 0 <= r < self.rows:
                    if self.grid[c][r] == TILE_BUILDING:
                        self.grid[c][r] = TILE_PARK

        # 6. Cache list of road nodes
        self.road_nodes = [
            (c, r) for c in range(self.cols) for r in range(self.rows) 
            if self.is_road(c, r)
        ]

    def is_road(self, c: int, r: int) -> bool:
        """Returns True if the grid coordinate is a drivable road."""
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.grid[c][r] in ROAD_COSTS
        return False

    def get_neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """
        Returns adjacent reachable road tiles and edge movement cost.
        Supports 4 cardinal directions (North, South, East, West).
        """
        c, r = node
        neighbors = []
        directions = [
            (0, -1), # North
            (0, 1),  # South
            (-1, 0), # West
            (1, 0),  # East
        ]

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
        
        # Breadth search around point
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
        self.path = path                       # Ordered list from start to goal
        self.total_cost = total_cost           # Total g(goal)
        self.visited_order = visited_order     # Nodes visited step-by-step for animation
        self.explored_count = explored_count   # Number of expanded nodes
        self.g_scores = g_scores               # Distance from start g(n) for each node
        self.f_scores = f_scores               # Total estimated cost f(n) = g(n) + h(n)


def a_star_search(
    city_map: CityMap, 
    start: Node, 
    goal: Node, 
    heuristic_type: str = "euclidean"
) -> Optional[AStarResult]:
    """
    Executes the classic A* Shortest Path Search on the City Graph.

    Formula:
        f(n) = g(n) + h(n)
        - g(n): Actual cost from start to current node n
        - h(n): Heuristic estimated cost from n to goal
        - f(n): Total estimated cost of path through n

    Returns:
        AStarResult object if path exists, None otherwise.
    """
    if start == goal:
        return AStarResult([start], 0.0, [start], 1, {start: 0.0}, {start: 0.0})

    # Pick heuristic
    h_func = heuristic_euclidean if heuristic_type == "euclidean" else heuristic_manhattan

    # Priority Queue elements: (f_score, counter, current_node)
    # Counter prevents comparison of nodes when f_scores are equal
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

        # GOAL CHECK: Reached destination
        if current == goal:
            # Reconstruct the path backwards from goal -> start
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

        # Explore all connected neighbors
        for neighbor, edge_cost in city_map.get_neighbors(current):
            tentative_g = g_score[current] + edge_cost

            # If this path to neighbor is better than any previous one
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h_val = h_func(neighbor, goal)
                f_val = tentative_g + h_val
                f_score[neighbor] = f_val

                counter += 1
                heapq.heappush(open_heap, (f_val, counter, neighbor))

    # Goal unreachable
    return None
