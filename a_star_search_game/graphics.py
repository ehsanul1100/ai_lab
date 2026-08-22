"""
=============================================================================
GRAPHICS & RENDERING ENGINE (PYGAME UI & ANIMATION)
=============================================================================
Handles all visual rendering, urban map drawing, A* search frontier bloom,
shortest path highlighting, vehicle journey animation, physics, and UI HUD.
=============================================================================
"""

import math
import pygame
from typing import List, Tuple, Optional, Dict
from core_logic import (
    CityMap, AStarResult, Node,
    TILE_ROAD_AVENUE, TILE_ROAD_STREET, TILE_ROAD_ALLEY,
    TILE_BUILDING, TILE_PARK, TILE_WATER
)

# Colors Palette (Cyber-Urban Night Navigator Theme)
COLOR_BG            = (16, 18, 24)
COLOR_GRID_LINE     = (24, 28, 38)
COLOR_SIDEBAR_BG    = (21, 24, 33)
COLOR_SIDEBAR_PANEL = (28, 33, 46)
COLOR_SIDEBAR_BORDER= (42, 50, 68)

COLOR_ROAD_AVENUE   = (34, 38, 50)
COLOR_ROAD_STREET   = (28, 32, 42)
COLOR_ROAD_ALLEY    = (24, 27, 36)
COLOR_LANE_MARK     = (75, 85, 110)

COLOR_BUILDING_BASE = (36, 40, 54)
COLOR_BUILDING_TOP  = (48, 54, 72)
COLOR_BUILDING_GLOW = (65, 75, 100)
COLOR_ROOF_ACCENT   = (75, 90, 125)

COLOR_PARK_BASE     = (20, 46, 35)
COLOR_PARK_TREE     = (30, 78, 55)

COLOR_START         = (46, 213, 115)    # Emerald Green
COLOR_GOAL          = (255, 71, 87)     # Crimson / Ruby
COLOR_VISITED       = (40, 95, 165, 70) # Translucent Blue Search Wave
COLOR_PATH_LINE     = (0, 240, 255)     # Electric Cyan
COLOR_TRAIL_LINE    = (255, 214, 10)    # Golden Yellow Traveled Path

COLOR_CAR_BODY      = (255, 204, 0)     # Vibrant Yellow Taxi / Sports Car
COLOR_CAR_ROOF      = (30, 35, 48)
COLOR_CAR_WHEEL     = (15, 15, 20)
COLOR_CAR_LIGHT     = (255, 252, 210, 85)

COLOR_TEXT_PRIMARY  = (240, 244, 252)
COLOR_TEXT_MUTED    = (135, 145, 170)
COLOR_TEXT_ACCENT   = (0, 220, 255)
COLOR_TEXT_GREEN    = (80, 230, 140)
COLOR_TEXT_RED      = (255, 100, 110)
COLOR_TEXT_GOLD     = (255, 215, 0)


class VehicleParticle:
    """Smoke/glow particle trailing the vehicle exhaust."""
    def __init__(self, x: float, y: float, angle: float):
        self.x = x
        self.y = y
        self.lifetime = 1.0
        self.decay = 0.06
        # Backward spread
        spread = 0.5
        speed = 0.7
        back_angle = angle + math.pi + (pygame.time.get_ticks() % 100 / 100.0 - 0.5) * spread
        self.vx = math.cos(back_angle) * speed
        self.vy = math.sin(back_angle) * speed
        self.radius = 3.5

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= self.decay
        self.radius = max(0.5, self.radius * 0.94)


class Visualizer:
    def __init__(self, screen: pygame.Surface, tile_size: int = 32, map_cols: int = 28, map_rows: int = 20):
        self.screen = screen
        self.tile_size = tile_size
        self.map_cols = map_cols
        self.map_rows = map_rows
        self.map_width = map_cols * tile_size
        self.map_height = map_rows * tile_size
        
        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)
        self.font_heading = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New, monospace", 12)
        self.font_small = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11)

        # Vehicle Animation Physics & State
        self.car_x: float = 0.0
        self.car_y: float = 0.0
        self.car_angle: float = 0.0        # Current smooth angle (radians)
        self.target_angle: float = 0.0     # Destination angle
        self.path_index: int = 0           # Current segment waypoint
        self.path_progress: float = 0.0    # 0.0 -> 1.0 along current segment
        self.particles: List[VehicleParticle] = []
        self.tire_tracks: List[Tuple[float, float]] = []

        # Pulse clock
        self.pulse_val = 0.0

    def grid_to_screen(self, col: int, row: int) -> Tuple[int, int]:
        """Convert grid coordinate (col, row) to tile center pixel (x, y)."""
        return (col * self.tile_size + self.tile_size // 2, 
                row * self.tile_size + self.tile_size // 2)

    def screen_to_grid(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        """Convert screen pixel to grid (col, row)."""
        if 0 <= px < self.map_width and 0 <= py < self.map_height:
            return (px // self.tile_size, py // self.tile_size)
        return None

    def reset_vehicle(self, start_node: Optional[Node]):
        """Reset vehicle to starting position."""
        if start_node:
            sx, sy = self.grid_to_screen(start_node[0], start_node[1])
            self.car_x = float(sx)
            self.car_y = float(sy)
            self.car_angle = 0.0
            self.target_angle = 0.0
        self.path_index = 0
        self.path_progress = 0.0
        self.particles.clear()
        self.tire_tracks.clear()

    # ==========================================
    # 1. MAP & URBAN ENVIRONMENT DRAWING
    # ==========================================

    def draw_city(self, city_map: CityMap):
        """Renders the roads, buildings, parks, and city blocks."""
        # 1. Fill base canvas
        pygame.draw.rect(self.screen, COLOR_BG, (0, 0, self.map_width, self.map_height))

        # 2. Roads & Terrain
        for c in range(city_map.cols):
            for r in range(city_map.rows):
                rect = (c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
                tile_type = city_map.grid[c][r]

                if tile_type == TILE_ROAD_AVENUE:
                    pygame.draw.rect(self.screen, COLOR_ROAD_AVENUE, rect)
                    # Avenue lane markings
                    cx, cy = c * self.tile_size + self.tile_size // 2, r * self.tile_size + self.tile_size // 2
                    pygame.draw.circle(self.screen, COLOR_LANE_MARK, (cx, cy), 1)

                elif tile_type == TILE_ROAD_STREET:
                    pygame.draw.rect(self.screen, COLOR_ROAD_STREET, rect)

                elif tile_type == TILE_ROAD_ALLEY:
                    pygame.draw.rect(self.screen, COLOR_ROAD_ALLEY, rect)

                elif tile_type == TILE_PARK:
                    pygame.draw.rect(self.screen, COLOR_PARK_BASE, rect)
                    cx, cy = c * self.tile_size + self.tile_size // 2, r * self.tile_size + self.tile_size // 2
                    pygame.draw.circle(self.screen, COLOR_PARK_TREE, (cx, cy), self.tile_size // 3)
                    pygame.draw.circle(self.screen, (38, 100, 70), (cx - 2, cy - 2), self.tile_size // 5)

                elif tile_type == TILE_WATER:
                    pygame.draw.rect(self.screen, (18, 55, 88), rect)

        # 3. 3D Isometric Buildings with Depth
        for c in range(city_map.cols):
            for r in range(city_map.rows):
                if city_map.grid[c][r] == TILE_BUILDING:
                    x = c * self.tile_size
                    y = r * self.tile_size
                    h = city_map.building_heights.get((c, r), 2)
                    color_idx = city_map.building_colors.get((c, r), 0)

                    pad = 2
                    bx, by = x + pad, y + pad
                    bw, bh = self.tile_size - pad * 2, self.tile_size - pad * 2

                    # Shadow
                    pygame.draw.rect(self.screen, (12, 14, 20), (bx, by, bw, bh))

                    wall_color = COLOR_BUILDING_BASE
                    top_color = COLOR_BUILDING_TOP
                    if color_idx == 1:
                        top_color = (55, 62, 82)
                    elif color_idx == 2:
                        top_color = (44, 58, 76)
                    elif color_idx == 3:
                        top_color = (50, 56, 66)

                    roof_shift = min(h * 2, 6)
                    pygame.draw.rect(self.screen, wall_color, (bx, by, bw, bh))
                    pygame.draw.rect(self.screen, top_color, (bx, by - roof_shift, bw, bh))
                    pygame.draw.rect(self.screen, COLOR_BUILDING_GLOW, (bx, by - roof_shift, bw, bh), 1)

                    if h >= 3:
                        rcx, rcy = bx + bw // 2, by - roof_shift + bh // 2
                        pygame.draw.rect(self.screen, COLOR_ROOF_ACCENT, (rcx - 3, rcy - 3, 6, 6))
                        if h == 4:
                            # Red rooftop safety beacon
                            pygame.draw.circle(self.screen, (255, 50, 50), (rcx, rcy), 2)

        # Border between Map and Sidebar
        pygame.draw.line(self.screen, COLOR_SIDEBAR_BORDER, (self.map_width, 0), (self.map_width, self.map_height), 2)

    # ==========================================
    # 2. A* SEARCH VISUALIZATION (WAVE & PATH)
    # ==========================================

    def draw_search_frontier(self, a_star_result: Optional[AStarResult]):
        """Renders explored nodes evaluated by A*."""
        if not a_star_result:
            return

        overlay = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        overlay.fill(COLOR_VISITED)

        for col, row in a_star_result.visited_order:
            self.screen.blit(overlay, (col * self.tile_size, row * self.tile_size))

    def draw_path(self, path: List[Node]):
        """Draws the planned shortest path and the dynamically completed golden trail."""
        if not path or len(path) < 2:
            return

        points = [self.grid_to_screen(c, r) for c, r in path]

        # 1. Planned cyan shortest path
        for offset_width in (8, 6, 4):
            pygame.draw.lines(self.screen, (0, 180, 240, 45), False, points, offset_width)
        pygame.draw.lines(self.screen, COLOR_PATH_LINE, False, points, 3)

        # 2. Traveled Golden Progress Trail (from start to car's current position)
        if self.path_index > 0 or self.path_progress > 0.0:
            traveled_pts = points[:self.path_index + 1]
            traveled_pts.append((int(self.car_x), int(self.car_y)))
            if len(traveled_pts) >= 2:
                pygame.draw.lines(self.screen, (255, 215, 0, 70), False, traveled_pts, 7)
                pygame.draw.lines(self.screen, COLOR_TRAIL_LINE, False, traveled_pts, 3)

        # 3. Waypoint Dots
        for pt in points:
            pygame.draw.circle(self.screen, (255, 255, 255), pt, 2)

    def draw_endpoints(self, start: Optional[Node], goal: Optional[Node], pulse_tick: int):
        """Draws glowing Start & Goal beacons."""
        self.pulse_val = (math.sin(pulse_tick * 0.08) + 1.0) * 0.5

        if start:
            sx, sy = self.grid_to_screen(start[0], start[1])
            pulse_rad = int(8 + self.pulse_val * 6)
            aura_surf = pygame.Surface((pulse_rad * 4, pulse_rad * 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (46, 213, 115, int(110 * (1.0 - self.pulse_val * 0.5))), (pulse_rad * 2, pulse_rad * 2), pulse_rad)
            self.screen.blit(aura_surf, (sx - pulse_rad * 2, sy - pulse_rad * 2))

            pygame.draw.circle(self.screen, COLOR_START, (sx, sy), 7)
            pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), 3)

            tag_surf = self.font_small.render("START", True, COLOR_TEXT_PRIMARY)
            self.screen.blit(tag_surf, (sx - tag_surf.get_width() // 2, sy - 18))

        if goal:
            gx, gy = self.grid_to_screen(goal[0], goal[1])
            pulse_rad = int(8 + self.pulse_val * 6)
            aura_surf = pygame.Surface((pulse_rad * 4, pulse_rad * 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 71, 87, int(110 * (1.0 - self.pulse_val * 0.5))), (pulse_rad * 2, pulse_rad * 2), pulse_rad)
            self.screen.blit(aura_surf, (gx - pulse_rad * 2, gy - pulse_rad * 2))

            pygame.draw.circle(self.screen, COLOR_GOAL, (gx, gy), 8, 2)
            pygame.draw.circle(self.screen, COLOR_GOAL, (gx, gy), 4)
            pygame.draw.circle(self.screen, (255, 255, 255), (gx, gy), 2)

            tag_surf = self.font_small.render("GOAL", True, COLOR_TEXT_PRIMARY)
            self.screen.blit(tag_surf, (gx - tag_surf.get_width() // 2, gy - 18))

    # ==========================================
    # 3. VEHICLE ANIMATION & PHYSICS
    # ==========================================

    def update_vehicle(self, path: List[Node], speed: float = 0.08) -> bool:
        """
        Updates the car position along the path waypoints.
        Returns True when arriving at final goal.
        """
        if not path or len(path) == 0:
            return False

        if len(path) == 1:
            cx, cy = self.grid_to_screen(path[0][0], path[0][1])
            self.car_x, self.car_y = float(cx), float(cy)
            return True

        if self.path_index >= len(path) - 1:
            fx, fy = self.grid_to_screen(path[-1][0], path[-1][1])
            self.car_x, self.car_y = float(fx), float(fy)
            return True

        curr_node = path[self.path_index]
        next_node = path[self.path_index + 1]

        x1, y1 = self.grid_to_screen(curr_node[0], curr_node[1])
        x2, y2 = self.grid_to_screen(next_node[0], next_node[1])

        # Step forward
        self.path_progress += speed
        if self.path_progress >= 1.0:
            self.path_progress = 0.0
            self.path_index += 1
            if self.path_index >= len(path) - 1:
                self.car_x, self.car_y = float(x2), float(y2)
                return True

        # Interpolate position
        self.car_x = x1 + (x2 - x1) * self.path_progress
        self.car_y = y1 + (y2 - y1) * self.path_progress

        # Angle heading calculation with smooth interpolation
        target_rad = math.atan2(y2 - y1, x2 - x1)
        # Normalize angular difference
        diff = (target_rad - self.car_angle + math.pi) % (2 * math.pi) - math.pi
        self.car_angle += diff * 0.25

        # Spawn exhaust particles
        if pygame.time.get_ticks() % 2 == 0:
            self.particles.append(VehicleParticle(self.car_x, self.car_y, self.car_angle))

        # Update active particles
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        return False

    def draw_vehicle(self):
        """Renders the moving vehicle, dynamic headlights beam, tires, and particle smoke."""
        # 1. Draw Exhaust Particles
        for p in self.particles:
            alpha = int(p.lifetime * 190)
            psurf = pygame.Surface((int(p.radius * 2) + 2, int(p.radius * 2) + 2), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (0, 220, 255, alpha), (int(p.radius) + 1, int(p.radius) + 1), int(p.radius))
            self.screen.blit(psurf, (p.x - p.radius - 1, p.y - p.radius - 1))

        # 2. Draw Dynamic Headlights Cone
        cone_length = 32
        cone_spread = 0.42
        p_left = (
            self.car_x + math.cos(self.car_angle - cone_spread) * cone_length,
            self.car_y + math.sin(self.car_angle - cone_spread) * cone_length
        )
        p_right = (
            self.car_x + math.cos(self.car_angle + cone_spread) * cone_length,
            self.car_y + math.sin(self.car_angle + cone_spread) * cone_length
        )
        headlight_surf = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(headlight_surf, COLOR_CAR_LIGHT, [(self.car_x, self.car_y), p_left, p_right])
        self.screen.blit(headlight_surf, (0, 0))

        # 3. Draw Detailed Sporty Vehicle Sprite (22 x 14)
        car_w, car_h = 22, 14
        car_surf = pygame.Surface((car_w, car_h), pygame.SRCALPHA)

        # Wheels (4 black corners)
        pygame.draw.rect(car_surf, COLOR_CAR_WHEEL, (3, 0, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, COLOR_CAR_WHEEL, (15, 0, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, COLOR_CAR_WHEEL, (3, 11, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, COLOR_CAR_WHEEL, (15, 11, 4, 3), border_radius=1)

        # Main Body Chassis
        pygame.draw.rect(car_surf, COLOR_CAR_BODY, (2, 2, 18, 10), border_radius=3)
        pygame.draw.rect(car_surf, (255, 230, 70), (3, 3, 16, 8), border_radius=2)

        # Cabin / Windshield
        pygame.draw.rect(car_surf, COLOR_CAR_ROOF, (7, 4, 8, 6), border_radius=1)
        pygame.draw.rect(car_surf, (100, 180, 240), (12, 5, 2, 4)) # Windshield glass

        # Roof Taxi Beacon
        pygame.draw.rect(car_surf, (255, 140, 0), (9, 5, 4, 4), border_radius=1)

        # Headlights (Front is +X in local surface)
        pygame.draw.rect(car_surf, (255, 255, 220), (19, 3, 2, 3))
        pygame.draw.rect(car_surf, (255, 255, 220), (19, 8, 2, 3))

        # Tail lights (Back is -X)
        pygame.draw.rect(car_surf, (255, 30, 30), (1, 3, 2, 2))
        pygame.draw.rect(car_surf, (255, 30, 30), (1, 9, 2, 2))

        # Rotate around center
        rotated = pygame.transform.rotate(car_surf, -math.degrees(self.car_angle))
        rect = rotated.get_rect(center=(int(self.car_x), int(self.car_y)))
        self.screen.blit(rotated, rect)

    # ==========================================
    # 4. SIDEBAR DASHBOARD & HUD TELEMETRY
    # ==========================================

    def draw_sidebar(
        self,
        state_text: str,
        start_node: Optional[Node],
        goal_node: Optional[Node],
        a_star_result: Optional[AStarResult],
        heuristic_name: str,
        speed_multiplier: float,
        is_traveling: bool,
        is_arrived: bool
    ):
        """Renders dashboard telemetry HUD on the right side."""
        sb_x = self.map_width
        sb_w = self.screen.get_width() - self.map_width
        sb_h = self.screen.get_height()

        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG, (sb_x, 0, sb_w, sb_h))

        # Title
        y = 18
        title_surf = self.font_title.render("A* CITY NAVIGATOR", True, COLOR_TEXT_ACCENT)
        self.screen.blit(title_surf, (sb_x + 20, y))
        y += 24
        sub_surf = self.font_small.render("AI Lab • Real-Time Journey Visualizer", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (sb_x + 20, y))
        y += 26

        # --- Status Badge ---
        badge_rect = pygame.Rect(sb_x + 18, y, sb_w - 36, 42)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, badge_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, badge_rect, 1, border_radius=6)

        status_color = COLOR_TEXT_ACCENT
        if "START" in state_text:
            status_color = COLOR_TEXT_GREEN
        elif "DESTINATION" in state_text or "GOAL" in state_text:
            status_color = COLOR_TEXT_RED
        elif is_traveling:
            status_color = COLOR_TEXT_GOLD
        elif is_arrived:
            status_color = COLOR_TEXT_GREEN

        status_title = self.font_small.render("NAVIGATION STATE", True, COLOR_TEXT_MUTED)
        status_val = self.font_heading.render(state_text, True, status_color)
        self.screen.blit(status_title, (sb_x + 28, y + 6))
        self.screen.blit(status_val, (sb_x + 28, y + 20))
        y += 54

        # --- Formula Card ---
        card_rect = pygame.Rect(sb_x + 18, y, sb_w - 36, 70)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, card_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, card_rect, 1, border_radius=6)

        card_title = self.font_heading.render("A* Evaluation Formula", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(card_title, (sb_x + 28, y + 6))
        f_form = self.font_mono.render("f(n) = g(n) + h(n)", True, COLOR_TEXT_ACCENT)
        self.screen.blit(f_form, (sb_x + 28, y + 26))
        desc = self.font_small.render("g: Road Cost  |  h: Estimated Distance", True, COLOR_TEXT_MUTED)
        self.screen.blit(desc, (sb_x + 28, y + 46))
        y += 82

        # --- Route Telemetry Card ---
        tele_rect = pygame.Rect(sb_x + 18, y, sb_w - 36, 172)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, tele_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, tele_rect, 1, border_radius=6)

        tele_title = self.font_heading.render("Live Journey Telemetry", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(tele_title, (sb_x + 28, y + 6))
        ty = y + 28

        start_str = f"({start_node[0]}, {start_node[1]})" if start_node else "--"
        goal_str  = f"({goal_node[0]}, {goal_node[1]})" if goal_node else "--"
        path_len_str = f"{len(a_star_result.path)} road tiles" if (a_star_result and a_star_result.path) else "--"
        cost_str     = f"{a_star_result.total_cost:.2f} cost units" if a_star_result else "--"
        explored_str = f"{a_star_result.explored_count} nodes" if a_star_result else "--"

        items = [
            ("Start Node:", start_str, COLOR_TEXT_GREEN if start_node else COLOR_TEXT_MUTED),
            ("Destination:", goal_str, COLOR_TEXT_RED if goal_node else COLOR_TEXT_MUTED),
            ("Heuristic:", heuristic_name.capitalize(), COLOR_TEXT_ACCENT),
            ("Explored Nodes:", explored_str, COLOR_TEXT_PRIMARY),
            ("Shortest Path Cost:", cost_str, COLOR_TEXT_GREEN if a_star_result else COLOR_TEXT_PRIMARY),
            ("Speed Multiplier:", f"{speed_multiplier:.1f}x", COLOR_TEXT_PRIMARY),
        ]

        for label, val, val_col in items:
            lbl_surf = self.font_small.render(label, True, COLOR_TEXT_MUTED)
            val_surf = self.font_small.render(val, True, val_col)
            self.screen.blit(lbl_surf, (sb_x + 28, ty))
            self.screen.blit(val_surf, (sb_x + 165, ty))
            ty += 21

        y += 184

        # --- Real-Time Progress Bar ---
        if a_star_result and a_star_result.path and len(a_star_result.path) > 1:
            total_steps = len(a_star_result.path) - 1
            cur_step = min(total_steps, self.path_index + self.path_progress)
            percent = min(1.0, cur_step / total_steps)

            prog_lbl = self.font_small.render(f"Journey Travel: {int(percent * 100)}% Completed", True, COLOR_TEXT_PRIMARY)
            self.screen.blit(prog_lbl, (sb_x + 28, y))

            bar_bg = pygame.Rect(sb_x + 28, y + 18, sb_w - 56, 8)
            pygame.draw.rect(self.screen, (40, 45, 60), bar_bg, border_radius=4)
            
            fill_w = int((sb_w - 56) * percent)
            if fill_w > 0:
                bar_fill = pygame.Rect(sb_x + 28, y + 18, fill_w, 8)
                bar_col = COLOR_START if is_arrived else COLOR_TRAIL_LINE
                pygame.draw.rect(self.screen, bar_col, bar_fill, border_radius=4)
            y += 36

        # --- Interactive Controls Box ---
        ctrl_rect = pygame.Rect(sb_x + 18, y, sb_w - 36, sb_h - y - 16)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, ctrl_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, ctrl_rect, 1, border_radius=6)

        ctrl_title = self.font_heading.render("Controls Guide", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(ctrl_title, (sb_x + 28, y + 6))
        cy = y + 28

        controls = [
            ("Click Map", "Pick Start & Destination"),
            ("Space", "Replay Travelling"),
            ("1 / 2 / 3", "Speed (1x, 2x, 4x)"),
            ("H", "Heuristic Toggle"),
            ("G", "Generate New City"),
            ("R", "Reset Selection"),
        ]

        for key, act in controls:
            k_surf = self.font_mono.render(f"[{key}]", True, COLOR_TEXT_ACCENT)
            a_surf = self.font_small.render(act, True, COLOR_TEXT_MUTED)
            self.screen.blit(k_surf, (sb_x + 28, cy))
            self.screen.blit(a_surf, (sb_x + 115, cy + 1))
            cy += 19
