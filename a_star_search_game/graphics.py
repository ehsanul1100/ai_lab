"""
=============================================================================
GRAPHICS & RENDERING ENGINE (VECTOR CARTOGRAPHY & MODERN UI)
=============================================================================
State-of-the-art visual renderer inspired by modern vector cartography
(Mapbox Dark & Mini Motorways):
  - Procedural road junctions with zebra crosswalks
  - Realistic airport tarmac with threshold piano-key markings & airplanes
  - Varied building architecture (helipads, glass atriums, HVACs, spires)
  - 3D shaded vector trees with specular highlights and ambient drop shadows
  - Waterways with stone embankments & animated wave crests
  - Laser route beam with glowing energy aura & dynamic vehicle lighting
  - Sleek modern glassmorphism sidebar HUD
=============================================================================
"""

import math
import pygame
from typing import List, Tuple, Optional, Dict
from core_logic import (
    CityMap, AStarResult, Node,
    TILE_ROAD_AVENUE, TILE_ROAD_STREET, TILE_ROAD_ALLEY, TILE_ROAD_BRIDGE,
    TILE_ROAD_BUSY, TILE_RUNWAY, TILE_ROADBLOCK, TILE_BUILDING, TILE_PARK,
    TILE_WATER, TILE_AIRPORT_TERMINAL,
    STYLE_AIRPORT, STYLE_BUSY_STREET, STYLE_METROPOLIS, STYLE_COASTAL,
    STYLE_OLD_TOWN, STYLE_CYBERPUNK, STYLE_RANDOM
)

# ==========================================
# MODERN CURATED COLOR PALETTE (MAPBOX DARK / MINIMALIST VECTOR)
# ==========================================
COLOR_BG            = (18, 21, 30)      # Deep Slate Land Canvas
COLOR_SIDEBAR_BG    = (22, 26, 38)      # Sidebar Charcoal
COLOR_SIDEBAR_PANEL = (28, 34, 50)      # Glassmorphism Card
COLOR_SIDEBAR_BORDER= (44, 54, 78)      # Card Border Trim
COLOR_SIDEBAR_HIGHLIGHT = (0, 229, 255) # Electric Cyan Accent

# Road Infrastructure
COLOR_ROAD_AVENUE   = (42, 48, 66)      # Broad Avenue Asphalt
COLOR_ROAD_STREET   = (32, 37, 52)      # Standard Street Asphalt
COLOR_ROAD_ALLEY    = (26, 30, 42)      # Narrow Alley Asphalt
COLOR_ROAD_BRIDGE   = (70, 82, 108)     # Steel/Concrete Bridge Deck
COLOR_ROAD_BUSY     = (62, 40, 24)      # Congested Amber Asphalt
COLOR_RUNWAY        = (22, 25, 34)      # Dark Tarmac Runway
COLOR_LANE_MARK     = (95, 108, 138)    # Road Lane Divider
COLOR_CROSSWALK     = (180, 195, 225)   # Zebra Crosswalk Stripes
COLOR_TAXIWAY_LINE  = (235, 185, 45)    # Airport Yellow Guide Line

# Water & Nature
COLOR_WATER_BASE    = (14, 38, 62)      # Deep Midnight Water
COLOR_WATER_WAVE    = (24, 60, 95)      # Wave Crest Highlight
COLOR_SHORELINE     = (28, 65, 95)      # Stone Quay Embankment
COLOR_PARK_BASE     = (22, 54, 38)      # Emerald Grassland Velvet
COLOR_PARK_BORDER   = (32, 75, 52)

# Tree Shading
COLOR_TREE_SHADOW   = (10, 26, 18, 140) # Translucent Shadow
COLOR_TREE_TRUNK    = (80, 52, 34)      # Wood Trunk
COLOR_TREE_DARK     = (26, 80, 50)      # Base Foliage
COLOR_TREE_MID      = (40, 122, 78)     # Mid Canopy
COLOR_TREE_LIGHT    = (75, 185, 115)    # Specular Sunlight Highlight
COLOR_PINE_DARK     = (20, 65, 45)
COLOR_PINE_LIGHT    = (45, 130, 85)

# 3D Architecture & Buildings
COLOR_BUILDING_SHADOW = (10, 12, 18)
COLOR_BUILDING_WALL   = (38, 44, 60)
COLOR_BUILDING_ROOF   = (50, 58, 80)
COLOR_ROOF_GLOW       = (68, 80, 110)
COLOR_ROOF_ACCENT     = (78, 92, 125)
COLOR_GLASS_TOWER     = (45, 75, 110)
COLOR_GLASS_REFLECT   = (90, 150, 210)
COLOR_HELIPAD_RING    = (240, 200, 30)

# A* Search & Vehicle Travel Visuals
COLOR_START           = (46, 213, 115)  # Emerald Green Beacon
COLOR_GOAL            = (255, 71, 87)   # Crimson Target
COLOR_VISITED         = (0, 180, 255, 45)# Translucent Search Wave
COLOR_PATH_LINE       = (0, 240, 255)   # Laser Neon Cyan
COLOR_TRAIL_LINE      = (255, 214, 10)  # Traveled Golden Path
COLOR_CAR_BODY        = (255, 204, 0)   # Golden Taxi / Sports Chassis
COLOR_CAR_LIGHT       = (255, 252, 215, 80) # Headlight Projection Beam

# UI Buttons & Typography
COLOR_BTN_NORMAL      = (34, 42, 60)
COLOR_BTN_HOVER       = (46, 58, 84)
COLOR_BTN_ACTIVE      = (0, 155, 215)
COLOR_TEXT_PRIMARY    = (242, 246, 255)
COLOR_TEXT_MUTED      = (135, 148, 175)
COLOR_TEXT_ACCENT     = (0, 225, 255)
COLOR_TEXT_GREEN      = (80, 230, 140)
COLOR_TEXT_RED        = (255, 100, 110)
COLOR_TEXT_GOLD       = (255, 215, 0)


class UIButton:
    """Clickable interactive UI button in sidebar HUD."""
    def __init__(self, rect: pygame.Rect, text: str, action_id: str, is_toggle: bool = False, active: bool = False):
        self.rect = rect
        self.text = text
        self.action_id = action_id
        self.is_toggle = is_toggle
        self.active = active
        self.hovered = False

    def check_hover(self, mx: int, my: int):
        self.hovered = self.rect.collidepoint(mx, my)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        bg_col = COLOR_BTN_NORMAL
        if self.active:
            bg_col = COLOR_BTN_ACTIVE
        elif self.hovered:
            bg_col = COLOR_BTN_HOVER

        pygame.draw.rect(screen, bg_col, self.rect, border_radius=5)
        border_col = (0, 220, 255) if (self.active or self.hovered) else COLOR_SIDEBAR_BORDER
        pygame.draw.rect(screen, border_col, self.rect, 1, border_radius=5)

        text_col = COLOR_TEXT_PRIMARY if not self.active else (255, 255, 255)
        txt_surf = font.render(self.text, True, text_col)
        screen.blit(txt_surf, (self.rect.centerx - txt_surf.get_width() // 2, 
                               self.rect.centery - txt_surf.get_height() // 2))


class VehicleParticle:
    """Smoke/glow particle trailing the vehicle exhaust."""
    def __init__(self, x: float, y: float, angle: float):
        self.x = x
        self.y = y
        self.lifetime = 1.0
        self.decay = 0.055
        spread = 0.45
        speed = 0.75
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
        
        # Typography
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 17, bold=True)
        self.font_heading = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 12)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New, monospace", 11)
        self.font_small = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 10)
        self.font_banner = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)

        # Vehicle Animation Physics & State
        self.car_x: float = 0.0
        self.car_y: float = 0.0
        self.car_angle: float = 0.0
        self.path_index: int = 0
        self.path_progress: float = 0.0
        self.particles: List[VehicleParticle] = []

        # Pulse clock & Water animation
        self.pulse_val = 0.0
        self.water_tick = 0

        # UI Buttons
        self.buttons: List[UIButton] = []
        self._init_ui_buttons()

    def _init_ui_buttons(self):
        """Constructs modern interactive sidebar buttons."""
        sb_x = self.map_width + 14
        sb_w = self.screen.get_width() - self.map_width - 28
        
        self.buttons.clear()

        # Presets (2 columns)
        btn_w = (sb_w - 6) // 2
        y = 104
        self.btn_preset_airport = UIButton(pygame.Rect(sb_x, y, btn_w, 22), "✈️ Airport Hub", "style_Airport Hub", is_toggle=True, active=True)
        self.btn_preset_traffic = UIButton(pygame.Rect(sb_x + btn_w + 6, y, btn_w, 22), "🚦 Busy Traffic", "style_Busy Traffic", is_toggle=True)
        y += 25
        self.btn_preset_metro   = UIButton(pygame.Rect(sb_x, y, btn_w, 22), "🏙️ Metropolis", "style_Metropolis", is_toggle=True)
        self.btn_preset_coast   = UIButton(pygame.Rect(sb_x + btn_w + 6, y, btn_w, 22), "🌊 Coastal River", "style_Coastal River", is_toggle=True)
        y += 25
        self.btn_preset_old     = UIButton(pygame.Rect(sb_x, y, btn_w, 22), "🏰 Old Town", "style_Old Town Maze", is_toggle=True)
        self.btn_preset_cyber   = UIButton(pygame.Rect(sb_x + btn_w + 6, y, btn_w, 22), "⚡ Cyberpunk", "style_Cyberpunk Grid", is_toggle=True)
        y += 27

        # Action: Randomize Map Button
        self.btn_gen_random = UIButton(pygame.Rect(sb_x, y, sb_w, 24), "🎲 Generate Random Sprawl", "gen_random")
        y += 28

        # Action: Replay & Reset Buttons
        self.btn_replay = UIButton(pygame.Rect(sb_x, y, btn_w, 24), "🔁 Replay Drive", "replay")
        self.btn_reset  = UIButton(pygame.Rect(sb_x + btn_w + 6, y, btn_w, 24), "🗑️ Reset Route", "reset")
        y += 27

        # Heuristic Toggle Button
        self.btn_heuristic = UIButton(pygame.Rect(sb_x, y, sb_w, 24), "🧭 Heuristic: Euclidean (H)", "toggle_heuristic")
        y += 27

        # Speed Selector Buttons (3 columns)
        sp_w = (sb_w - 10) // 3
        self.btn_sp1 = UIButton(pygame.Rect(sb_x, y, sp_w, 22), "1x Speed", "speed_1", is_toggle=True, active=True)
        self.btn_sp2 = UIButton(pygame.Rect(sb_x + sp_w + 5, y, sp_w, 22), "2x Speed", "speed_2", is_toggle=True)
        self.btn_sp4 = UIButton(pygame.Rect(sb_x + (sp_w + 5) * 2, y, sp_w, 22), "4x Speed", "speed_4", is_toggle=True)

        self.buttons.extend([
            self.btn_preset_airport, self.btn_preset_traffic,
            self.btn_preset_metro, self.btn_preset_coast, self.btn_preset_old, self.btn_preset_cyber,
            self.btn_gen_random, self.btn_replay, self.btn_reset, self.btn_heuristic,
            self.btn_sp1, self.btn_sp2, self.btn_sp4
        ])

    def handle_mouse_motion(self, mx: int, my: int):
        for btn in self.buttons:
            btn.check_hover(mx, my)

    def handle_click(self, mx: int, my: int) -> Optional[str]:
        for btn in self.buttons:
            if btn.rect.collidepoint(mx, my):
                return btn.action_id
        return None

    def grid_to_screen(self, col: int, row: int) -> Tuple[int, int]:
        return (col * self.tile_size + self.tile_size // 2, 
                row * self.tile_size + self.tile_size // 2)

    def screen_to_grid(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        if 0 <= px < self.map_width and 0 <= py < self.map_height:
            return (px // self.tile_size, py // self.tile_size)
        return None

    def reset_vehicle(self, start_node: Optional[Node]):
        if start_node:
            sx, sy = self.grid_to_screen(start_node[0], start_node[1])
            self.car_x = float(sx)
            self.car_y = float(sy)
            self.car_angle = 0.0
        self.path_index = 0
        self.path_progress = 0.0
        self.particles.clear()

    # ==========================================
    # 1. MAP & URBAN ENVIRONMENT DRAWING
    # ==========================================

    def draw_city(self, city_map: CityMap):
        """Renders roads, crosswalks, airport tarmac, buildings, water, and trees."""
        self.water_tick += 1
        pygame.draw.rect(self.screen, COLOR_BG, (0, 0, self.map_width, self.map_height))

        # --- Pass 1: Terrain, Water, Roads, Runways, Bridges ---
        for c in range(city_map.cols):
            for r in range(city_map.rows):
                rect = (c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
                tile_type = city_map.grid[c][r]
                cx, cy = c * self.tile_size + self.tile_size // 2, r * self.tile_size + self.tile_size // 2

                # 1. WATER & EMBANKMENT
                if tile_type == TILE_WATER:
                    pygame.draw.rect(self.screen, COLOR_WATER_BASE, rect)
                    # Quayside shoreline border
                    for dc, dr in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nc, nr = c + dc, r + dr
                        if 0 <= nc < city_map.cols and 0 <= nr < city_map.rows:
                            if city_map.grid[nc][nr] != TILE_WATER and city_map.grid[nc][nr] != TILE_ROAD_BRIDGE:
                                if dc == -1: pygame.draw.line(self.screen, COLOR_SHORELINE, (rect[0], rect[1]), (rect[0], rect[1]+rect[3]), 2)
                                elif dc == 1: pygame.draw.line(self.screen, COLOR_SHORELINE, (rect[0]+rect[2], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), 2)
                                elif dr == -1: pygame.draw.line(self.screen, COLOR_SHORELINE, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]), 2)
                                elif dr == 1: pygame.draw.line(self.screen, COLOR_SHORELINE, (rect[0], rect[1]+rect[3]), (rect[0]+rect[2], rect[1]+rect[3]), 2)
                    
                    # Animated Wave Crests
                    wave_offset = int(math.sin((c * 1.5 + r * 2.0 + self.water_tick * 0.06)) * 3)
                    wx = c * self.tile_size + 4
                    wy = r * self.tile_size + 14 + wave_offset
                    pygame.draw.line(self.screen, COLOR_WATER_WAVE, (wx, wy), (wx + self.tile_size - 8, wy), 1)

                # 2. AIRPORT RUNWAY & TAXIWAY
                elif tile_type == TILE_RUNWAY:
                    pygame.draw.rect(self.screen, COLOR_RUNWAY, rect)
                    # Edge marker lights
                    pygame.draw.circle(self.screen, (240, 245, 255), (rect[0] + 2, rect[1] + 2), 1)
                    pygame.draw.circle(self.screen, (240, 245, 255), (rect[0] + rect[2] - 2, rect[1] + 2), 1)
                    pygame.draw.circle(self.screen, (240, 245, 255), (rect[0] + 2, rect[1] + rect[3] - 2), 1)
                    pygame.draw.circle(self.screen, (240, 245, 255), (rect[0] + rect[2] - 2, rect[1] + rect[3] - 2), 1)
                    
                    # Centerline threshold dashes
                    pygame.draw.line(self.screen, (245, 245, 255), (cx - 9, cy), (cx + 9, cy), 2)
                    # Yellow Taxiway guidance lines
                    pygame.draw.line(self.screen, COLOR_TAXIWAY_LINE, (rect[0] + 4, cy + 8), (rect[0] + rect[2] - 4, cy + 8), 1)

                # 3. BUSY CONGESTED STREETS
                elif tile_type == TILE_ROAD_BUSY:
                    pygame.draw.rect(self.screen, COLOR_ROAD_BUSY, rect)
                    # Traffic warning pulse
                    pulse_t = (math.sin(self.water_tick * 0.1 + c + r) + 1.0) * 0.5
                    alpha_val = int(80 + pulse_t * 80)
                    pygame.draw.circle(self.screen, (255, 140, 20), (cx, cy), 3)

                # 4. BRIDGE OVER WATER
                elif tile_type == TILE_ROAD_BRIDGE:
                    pygame.draw.rect(self.screen, COLOR_WATER_BASE, rect)
                    # Deck
                    pygame.draw.rect(self.screen, COLOR_ROAD_BRIDGE, (rect[0], rect[1] + 4, rect[2], rect[3] - 8))
                    # Steel Railings & Trusses
                    pygame.draw.line(self.screen, (190, 210, 235), (rect[0], rect[1] + 4), (rect[0] + rect[2], rect[1] + 4), 2)
                    pygame.draw.line(self.screen, (190, 210, 235), (rect[0], rect[1] + rect[3] - 4), (rect[0] + rect[2], rect[1] + rect[3] - 4), 2)
                    # Suspension cables
                    pygame.draw.line(self.screen, (130, 150, 180), (cx, rect[1] + 4), (cx, rect[1] + rect[3] - 4), 1)

                # 5. MAJOR AVENUE
                elif tile_type == TILE_ROAD_AVENUE:
                    pygame.draw.rect(self.screen, COLOR_ROAD_AVENUE, rect)
                    # Double center dash
                    pygame.draw.circle(self.screen, COLOR_LANE_MARK, (cx, cy), 1)

                # 6. REGULAR STREET & ALLEY
                elif tile_type == TILE_ROAD_STREET:
                    pygame.draw.rect(self.screen, COLOR_ROAD_STREET, rect)
                elif tile_type == TILE_ROAD_ALLEY:
                    pygame.draw.rect(self.screen, COLOR_ROAD_ALLEY, rect)

                # 7. PARKS & GREENERY
                elif tile_type == TILE_PARK:
                    pygame.draw.rect(self.screen, COLOR_PARK_BASE, rect)
                    pygame.draw.rect(self.screen, COLOR_PARK_BORDER, rect, 1)

                # 8. AIRPORT TERMINAL CONCOURSE
                elif tile_type == TILE_AIRPORT_TERMINAL:
                    pygame.draw.rect(self.screen, (24, 32, 48), rect)
                    pygame.draw.rect(self.screen, COLOR_GLASS_TOWER, (rect[0] + 2, rect[1] + 2, rect[2] - 4, rect[3] - 4), border_radius=3)
                    # Glass reflection
                    pygame.draw.line(self.screen, COLOR_GLASS_REFLECT, (rect[0] + 4, rect[1] + 4), (rect[0] + rect[2] - 6, rect[1] + 4), 1)
                    # Radar Tower Beacon
                    radar_angle = self.water_tick * 0.1
                    rx = cx + int(math.cos(radar_angle) * 4)
                    ry = cy + int(math.sin(radar_angle) * 4)
                    pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 3)
                    pygame.draw.circle(self.screen, (0, 220, 255), (rx, ry), 1)

        # --- Pass 1.5: Road Junctions & Zebra Crosswalks ---
        for c in range(1, city_map.cols - 1):
            for r in range(1, city_map.rows - 1):
                if city_map.is_road(c, r):
                    # Check if junction (3 or 4 connected roads)
                    adj_roads = sum(1 for dc, dr in [(-1,0), (1,0), (0,-1), (0,1)] if city_map.is_road(c+dc, r+dr))
                    if adj_roads >= 3:
                        x = c * self.tile_size
                        y = r * self.tile_size
                        # Zebra crosswalk marks on junction perimeter
                        for i in range(2, self.tile_size - 2, 4):
                            pygame.draw.line(self.screen, COLOR_CROSSWALK, (x + i, y + 2), (x + i + 2, y + 2), 1)
                            pygame.draw.line(self.screen, COLOR_CROSSWALK, (x + i, y + self.tile_size - 3), (x + i + 2, y + self.tile_size - 3), 1)

        # --- Pass 2: 3D Isometric Buildings with Varied Architecture ---
        for c in range(city_map.cols):
            for r in range(city_map.rows):
                if city_map.grid[c][r] == TILE_BUILDING:
                    x = c * self.tile_size
                    y = r * self.tile_size
                    h = city_map.building_heights.get((c, r), 2)
                    b_type = city_map.building_types.get((c, r), 0)

                    pad = 2
                    bx, by = x + pad, y + pad
                    bw, bh = self.tile_size - pad * 2, self.tile_size - pad * 2
                    roof_shift = min(h * 2, 6)

                    # Ambient Base Shadow
                    pygame.draw.rect(self.screen, COLOR_BUILDING_SHADOW, (bx, by, bw, bh))

                    # 3D Wall
                    wall_color = COLOR_BUILDING_WALL
                    pygame.draw.rect(self.screen, wall_color, (bx, by, bw, bh))

                    # Roof Types
                    roof_y = by - roof_shift
                    roof_rect = (bx, roof_y, bw, bh)

                    if b_type == 1:
                        # Helipad Building
                        pygame.draw.rect(self.screen, (45, 52, 70), roof_rect)
                        pygame.draw.rect(self.screen, COLOR_ROOF_GLOW, roof_rect, 1)
                        rcx, rcy = bx + bw // 2, roof_y + bh // 2
                        pygame.draw.circle(self.screen, COLOR_HELIPAD_RING, (rcx, rcy), 6, 1)
                        # 'H' symbol
                        pygame.draw.line(self.screen, COLOR_HELIPAD_RING, (rcx - 3, rcy - 3), (rcx - 3, rcy + 3), 1)
                        pygame.draw.line(self.screen, COLOR_HELIPAD_RING, (rcx + 3, rcy - 3), (rcx + 3, rcy + 3), 1)
                        pygame.draw.line(self.screen, COLOR_HELIPAD_RING, (rcx - 3, rcy), (rcx + 3, rcy), 1)

                    elif b_type == 2:
                        # Glass Skyscraper with Skylight Grid
                        pygame.draw.rect(self.screen, COLOR_GLASS_TOWER, roof_rect)
                        pygame.draw.rect(self.screen, COLOR_GLASS_REFLECT, roof_rect, 1)
                        # Skylight cross hatch
                        pygame.draw.line(self.screen, COLOR_GLASS_REFLECT, (bx + 4, roof_y + 4), (bx + bw - 4, roof_y + bh - 4), 1)
                        pygame.draw.line(self.screen, COLOR_GLASS_REFLECT, (bx + bw - 4, roof_y + 4), (bx + 4, roof_y + bh - 4), 1)

                    elif b_type == 3:
                        # Residential Complex with Courtyard
                        pygame.draw.rect(self.screen, (42, 50, 68), roof_rect)
                        pygame.draw.rect(self.screen, COLOR_ROOF_GLOW, roof_rect, 1)
                        # Inner terrace
                        pygame.draw.rect(self.screen, (28, 34, 48), (bx + 4, roof_y + 4, bw - 8, bh - 8))

                    else:
                        # Standard Highrise with Rooftop HVAC & Antenna
                        pygame.draw.rect(self.screen, COLOR_BUILDING_ROOF, roof_rect)
                        pygame.draw.rect(self.screen, COLOR_ROOF_GLOW, roof_rect, 1)
                        rcx, rcy = bx + bw // 2, roof_y + bh // 2
                        pygame.draw.rect(self.screen, COLOR_ROOF_ACCENT, (rcx - 3, rcy - 3, 6, 6))

                    # Aviation Red Safety Beacon on Taller Towers
                    if h >= 3:
                        rcx, rcy = bx + bw // 2, roof_y + bh // 2
                        beacon_pulse = (math.sin(self.water_tick * 0.15 + c * 3 + r) + 1.0) * 0.5
                        if beacon_pulse > 0.4:
                            pygame.draw.circle(self.screen, (255, 50, 50), (rcx, rcy - 2), 2)

        # --- Pass 3: Lush Shaded Vector Trees ---
        for tx, ty, tree_type in city_map.trees:
            px = int(tx * self.tile_size)
            py = int(ty * self.tile_size)

            # Drop Shadow
            shadow_surf = pygame.Surface((14, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (10, 24, 16, 130), (0, 0, 14, 8))
            self.screen.blit(shadow_surf, (px - 7, py - 2))

            # Trunk
            pygame.draw.line(self.screen, COLOR_TREE_TRUNK, (px, py), (px, py - 4), 2)

            # Shaded Spherical / Pine Canopy
            if tree_type == 2:
                # Pine Tree (Conical layered triangles)
                pygame.draw.polygon(self.screen, COLOR_PINE_DARK, [(px, py - 12), (px - 5, py - 4), (px + 5, py - 4)])
                pygame.draw.polygon(self.screen, COLOR_PINE_LIGHT, [(px, py - 12), (px - 2, py - 4), (px + 4, py - 4)])
            else:
                # Deciduous Tree (Layered 3D Spherical Volume)
                rad = 6 if tree_type == 1 else 5
                cy_tree = py - 6
                # Base dark leaf sphere
                pygame.draw.circle(self.screen, COLOR_TREE_DARK, (px, cy_tree), rad)
                # Mid tone layer
                pygame.draw.circle(self.screen, COLOR_TREE_MID, (px - 1, cy_tree - 1), rad - 1)
                # Specular sunlight highlight (Top-left sun source)
                pygame.draw.circle(self.screen, COLOR_TREE_LIGHT, (px - 2, cy_tree - 2), max(1, rad // 2))

        # Map Border Divider
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

        # 1. Planned Cyan Laser Path with Aura
        for offset_width in (9, 6, 4):
            pygame.draw.lines(self.screen, (0, 190, 255, 40), False, points, offset_width)
        pygame.draw.lines(self.screen, COLOR_PATH_LINE, False, points, 3)

        # 2. Traveled Golden Progress Trail
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

    def draw_startup_prompt(self):
        """Displays guidance banner when no points are selected."""
        overlay_w, overlay_h = 360, 44
        ox = (self.map_width - overlay_w) // 2
        oy = self.map_height - 60

        surf = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 24, 35, 220), (0, 0, overlay_w, overlay_h), border_radius=8)
        pygame.draw.rect(surf, (0, 220, 255, 180), (0, 0, overlay_w, overlay_h), 1, border_radius=8)

        txt = self.font_banner.render("📍 Click ANY Road to Set START Point", True, COLOR_TEXT_ACCENT)
        surf.blit(txt, (overlay_w // 2 - txt.get_width() // 2, overlay_h // 2 - txt.get_height() // 2))
        self.screen.blit(surf, (ox, oy))

    # ==========================================
    # 3. VEHICLE ANIMATION & PHYSICS
    # ==========================================

    def update_vehicle(self, path: List[Node], speed: float = 0.08) -> bool:
        """Updates car position along waypoints. Returns True on arrival."""
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

        self.path_progress += speed
        if self.path_progress >= 1.0:
            self.path_progress = 0.0
            self.path_index += 1
            if self.path_index >= len(path) - 1:
                self.car_x, self.car_y = float(x2), float(y2)
                return True

        self.car_x = x1 + (x2 - x1) * self.path_progress
        self.car_y = y1 + (y2 - y1) * self.path_progress

        target_rad = math.atan2(y2 - y1, x2 - x1)
        diff = (target_rad - self.car_angle + math.pi) % (2 * math.pi) - math.pi
        self.car_angle += diff * 0.25

        if pygame.time.get_ticks() % 2 == 0:
            self.particles.append(VehicleParticle(self.car_x, self.car_y, self.car_angle))

        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        return False

    def draw_vehicle(self):
        """Renders the vehicle, headlights, tires, and smoke particles."""
        # 1. Exhaust particles
        for p in self.particles:
            alpha = int(p.lifetime * 190)
            psurf = pygame.Surface((int(p.radius * 2) + 2, int(p.radius * 2) + 2), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (0, 220, 255, alpha), (int(p.radius) + 1, int(p.radius) + 1), int(p.radius))
            self.screen.blit(psurf, (p.x - p.radius - 1, p.y - p.radius - 1))

        # 2. Dynamic Realistic Headlights
        cone_length = 34
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

        # 3. Vehicle Sprite (Sports Taxi)
        car_w, car_h = 22, 14
        car_surf = pygame.Surface((car_w, car_h), pygame.SRCALPHA)

        # Tires
        pygame.draw.rect(car_surf, (15, 15, 20), (3, 0, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, (15, 15, 20), (15, 0, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, (15, 15, 20), (3, 11, 4, 3), border_radius=1)
        pygame.draw.rect(car_surf, (15, 15, 20), (15, 11, 4, 3), border_radius=1)

        # Metallic Yellow Body
        pygame.draw.rect(car_surf, COLOR_CAR_BODY, (2, 2, 18, 10), border_radius=3)
        pygame.draw.rect(car_surf, (255, 235, 80), (3, 3, 16, 8), border_radius=2)

        # Tinted Glass Cabin
        pygame.draw.rect(car_surf, (28, 34, 46), (7, 4, 8, 6), border_radius=1)
        pygame.draw.rect(car_surf, (110, 190, 255), (12, 5, 2, 4))
        # Taxi Amber Beacon
        pygame.draw.rect(car_surf, (255, 140, 0), (9, 5, 4, 4), border_radius=1)

        # Lights
        pygame.draw.rect(car_surf, (255, 255, 230), (19, 3, 2, 3))
        pygame.draw.rect(car_surf, (255, 255, 230), (19, 8, 2, 3))
        pygame.draw.rect(car_surf, (255, 35, 35), (1, 3, 2, 2))
        pygame.draw.rect(car_surf, (255, 35, 35), (1, 9, 2, 2))

        rotated = pygame.transform.rotate(car_surf, -math.degrees(self.car_angle))
        rect = rotated.get_rect(center=(int(self.car_x), int(self.car_y)))
        self.screen.blit(rotated, rect)

    # ==========================================
    # 4. SIDEBAR DASHBOARD & INTERACTIVE HUD
    # ==========================================

    def draw_sidebar(
        self,
        state_text: str,
        start_node: Optional[Node],
        goal_node: Optional[Node],
        a_star_result: Optional[AStarResult],
        heuristic_name: str,
        speed_multiplier: float,
        current_city_style: str,
        is_traveling: bool,
        is_arrived: bool
    ):
        """Renders interactive buttons, state telemetry, and controls in the right sidebar."""
        sb_x = self.map_width
        sb_w = self.screen.get_width() - self.map_width
        sb_h = self.screen.get_height()

        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG, (sb_x, 0, sb_w, sb_h))

        # Header Title
        y = 12
        title_surf = self.font_title.render("A* CITY NAVIGATOR", True, COLOR_TEXT_ACCENT)
        self.screen.blit(title_surf, (sb_x + 16, y))
        y += 20
        sub_surf = self.font_small.render("AI Lab • Urban Pathfinding Simulation", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (sb_x + 16, y))
        y += 20

        # --- Status Badge Box ---
        badge_rect = pygame.Rect(sb_x + 14, y, sb_w - 28, 36)
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

        status_title = self.font_small.render("STATUS:", True, COLOR_TEXT_MUTED)
        status_val = self.font_heading.render(state_text, True, status_color)
        self.screen.blit(status_title, (sb_x + 22, y + 3))
        self.screen.blit(status_val, (sb_x + 22, y + 16))
        y += 42

        # Section Header: City Map Presets
        sec_title = self.font_heading.render("City Presets & UI Controls", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(sec_title, (sb_x + 16, y))

        # Update button active states
        self.btn_preset_airport.active = (current_city_style == STYLE_AIRPORT)
        self.btn_preset_traffic.active = (current_city_style == STYLE_BUSY_STREET)
        self.btn_preset_metro.active   = (current_city_style == STYLE_METROPOLIS)
        self.btn_preset_coast.active   = (current_city_style == STYLE_COASTAL)
        self.btn_preset_old.active     = (current_city_style == STYLE_OLD_TOWN)
        self.btn_preset_cyber.active   = (current_city_style == STYLE_CYBERPUNK)
        
        self.btn_sp1.active = (speed_multiplier == 1.0)
        self.btn_sp2.active = (speed_multiplier == 2.0)
        self.btn_sp4.active = (speed_multiplier == 4.0)
        self.btn_heuristic.text = f"🧭 Heuristic: {heuristic_name.capitalize()} (H)"

        # Draw all interactive UI Buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.font_small)

        y = 314

        # --- Route Telemetry Card ---
        tele_rect = pygame.Rect(sb_x + 14, y, sb_w - 28, 138)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, tele_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, tele_rect, 1, border_radius=6)

        tele_title = self.font_heading.render("Live Route Telemetry", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(tele_title, (sb_x + 22, y + 6))
        ty = y + 26

        start_str = f"({start_node[0]}, {start_node[1]})" if start_node else "Not Selected"
        goal_str  = f"({goal_node[0]}, {goal_node[1]})" if goal_node else "Not Selected"
        path_len_str = f"{len(a_star_result.path)} tiles" if (a_star_result and a_star_result.path) else "--"
        cost_str     = f"{a_star_result.total_cost:.2f} cost units" if a_star_result else "--"
        explored_str = f"{a_star_result.explored_count} nodes" if a_star_result else "--"

        items = [
            ("Start Node:", start_str, COLOR_TEXT_GREEN if start_node else COLOR_TEXT_MUTED),
            ("Destination:", goal_str, COLOR_TEXT_RED if goal_node else COLOR_TEXT_MUTED),
            ("Explored Nodes:", explored_str, COLOR_TEXT_PRIMARY),
            ("A* Shortest Cost:", cost_str, COLOR_TEXT_GREEN if a_star_result else COLOR_TEXT_PRIMARY),
            ("Formula:", "f(n) = g(n) + h(n)", COLOR_TEXT_ACCENT)
        ]

        for label, val, val_col in items:
            lbl_surf = self.font_small.render(label, True, COLOR_TEXT_MUTED)
            val_surf = self.font_small.render(val, True, val_col)
            self.screen.blit(lbl_surf, (sb_x + 22, ty))
            self.screen.blit(val_surf, (sb_x + 148, ty))
            ty += 21

        y += 146

        # --- Real-Time Progress Bar ---
        if a_star_result and a_star_result.path and len(a_star_result.path) > 1:
            total_steps = len(a_star_result.path) - 1
            cur_step = min(total_steps, self.path_index + self.path_progress)
            percent = min(1.0, cur_step / total_steps)

            prog_lbl = self.font_small.render(f"Journey: {int(percent * 100)}% Completed", True, COLOR_TEXT_PRIMARY)
            self.screen.blit(prog_lbl, (sb_x + 22, y))

            bar_bg = pygame.Rect(sb_x + 22, y + 16, sb_w - 44, 6)
            pygame.draw.rect(self.screen, (40, 45, 60), bar_bg, border_radius=3)
            
            fill_w = int((sb_w - 44) * percent)
            if fill_w > 0:
                bar_fill = pygame.Rect(sb_x + 22, y + 16, fill_w, 6)
                bar_col = COLOR_START if is_arrived else COLOR_TRAIL_LINE
                pygame.draw.rect(self.screen, bar_col, bar_fill, border_radius=3)
            y += 28

        # --- Quick Legend Box ---
        leg_rect = pygame.Rect(sb_x + 14, y, sb_w - 28, sb_h - y - 12)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_PANEL, leg_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BORDER, leg_rect, 1, border_radius=6)

        leg_title = self.font_heading.render("Map Legend & Weights", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(leg_title, (sb_x + 22, y + 5))
        ly = y + 24

        legend_items = [
            (COLOR_ROAD_AVENUE, "Avenue / Highway (Cost: 1.0)"),
            (COLOR_RUNWAY, "Airport Runway (Cost: 1.0)"),
            (COLOR_ROAD_BRIDGE, "Bridge Over River (Cost: 1.2)"),
            (COLOR_ROAD_STREET, "City Street (Cost: 1.5)"),
            (COLOR_ROAD_BUSY, "Busy Traffic (Cost: 3.5)"),
            (COLOR_TREE_MID, "Roadside / Park Trees"),
        ]

        for col, desc_text in legend_items:
            pygame.draw.circle(self.screen, col, (sb_x + 28, ly + 6), 4)
            d_surf = self.font_small.render(desc_text, True, COLOR_TEXT_MUTED)
            self.screen.blit(d_surf, (sb_x + 38, ly))
            ly += 16
