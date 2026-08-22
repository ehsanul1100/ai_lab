"""
=============================================================================
A* SEARCH CITY PATHFINDING GAME - MAIN ENTRY POINT
=============================================================================
Run this file to launch the interactive simulation game.

Usage:
  python main.py

Controls:
  - Mouse Left Click : Select Start Point, then select Destination
  - [SPACE]          : Replay Travel Animation
  - [1 / 2 / 3]      : Set Travel Speed (1x, 2x, 4x)
  - [H]              : Toggle Heuristic (Euclidean <-> Manhattan)
  - [G]              : Generate New City Layout
  - [R]              : Reset Selection
=============================================================================
"""

import sys
import pygame
from core_logic import CityMap, a_star_search, AStarResult, Node
from graphics import Visualizer

# Window Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 640
TILE_SIZE = 32

MAP_COLS = 28
MAP_ROWS = 20

# State Constants
STATE_SELECT_START = "SELECT START POINT"
STATE_SELECT_GOAL = "SELECT DESTINATION"
STATE_TRAVELLING = "TRAVELLING TO GOAL"
STATE_ARRIVED = "ARRIVED AT DESTINATION"


def main():
    pygame.init()
    pygame.display.set_caption("A* Search Algorithm - Dense City Navigator")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Initialize City Map & Visualizer Engine
    city_map = CityMap(cols=MAP_COLS, rows=MAP_ROWS)
    visualizer = Visualizer(screen, tile_size=TILE_SIZE, map_cols=MAP_COLS, map_rows=MAP_ROWS)

    # Game State Variables
    start_node: Node = None
    goal_node: Node = None
    a_star_result: AStarResult = None
    
    current_state = STATE_SELECT_START
    heuristic_type = "euclidean"
    base_speed = 0.08
    speed_multiplier = 1.0
    is_traveling = False
    is_arrived = False

    # Choose default initial demo points so game opens with an active trip
    if len(city_map.road_nodes) >= 2:
        start_node = city_map.road_nodes[0]
        goal_node = city_map.road_nodes[-1]
        a_star_result = a_star_search(city_map, start_node, goal_node, heuristic_type)
        visualizer.reset_vehicle(start_node)
        current_state = STATE_TRAVELLING
        is_traveling = True

    running = True
    pulse_tick = 0

    while running:
        pulse_tick += 1
        dt = clock.tick(60)

        # -------------------------------------------------------------
        # 1. EVENT HANDLING
        # -------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left Click on Map
                mx, my = pygame.mouse.get_pos()
                grid_pos = visualizer.screen_to_grid(mx, my)

                if grid_pos is not None:
                    # Snap click to nearest drivable road intersection
                    road_node = city_map.get_nearest_road(grid_pos[0], grid_pos[1])

                    if road_node:
                        if current_state in (STATE_SELECT_START, STATE_ARRIVED) or start_node is None:
                            # 1st Click: Select Start
                            start_node = road_node
                            goal_node = None
                            a_star_result = None
                            is_traveling = False
                            is_arrived = False
                            visualizer.reset_vehicle(start_node)
                            current_state = STATE_SELECT_GOAL

                        elif current_state == STATE_SELECT_GOAL or (start_node is not None and goal_node is None):
                            # 2nd Click: Select Goal & Run A* Search
                            goal_node = road_node
                            a_star_result = a_star_search(city_map, start_node, goal_node, heuristic_type)
                            visualizer.reset_vehicle(start_node)
                            
                            if a_star_result and a_star_result.path:
                                current_state = STATE_TRAVELLING
                                is_traveling = True
                                is_arrived = False
                            else:
                                current_state = "NO PATH FOUND"
                                is_traveling = False

                        elif current_state == STATE_TRAVELLING:
                            # Dynamic Re-routing: Change goal on the fly
                            goal_node = road_node
                            a_star_result = a_star_search(city_map, start_node, goal_node, heuristic_type)
                            visualizer.reset_vehicle(start_node)
                            is_traveling = True
                            is_arrived = False

            elif event.type == pygame.KEYDOWN:
                # [R] Reset Selection
                if event.key == pygame.K_r:
                    start_node = None
                    goal_node = None
                    a_star_result = None
                    is_traveling = False
                    is_arrived = False
                    visualizer.reset_vehicle(None)
                    current_state = STATE_SELECT_START

                # [SPACE] Replay Journey Animation
                elif event.key == pygame.K_SPACE:
                    if a_star_result and a_star_result.path:
                        visualizer.reset_vehicle(start_node)
                        is_traveling = True
                        is_arrived = False
                        current_state = STATE_TRAVELLING

                # [G] Generate Fresh Procedural City
                elif event.key == pygame.K_g:
                    city_map = CityMap(cols=MAP_COLS, rows=MAP_ROWS)
                    start_node = None
                    goal_node = None
                    a_star_result = None
                    is_traveling = False
                    is_arrived = False
                    visualizer.reset_vehicle(None)
                    current_state = STATE_SELECT_START

                # [H] Toggle Heuristic Function
                elif event.key == pygame.K_h:
                    heuristic_type = "manhattan" if heuristic_type == "euclidean" else "euclidean"
                    if start_node and goal_node:
                        a_star_result = a_star_search(city_map, start_node, goal_node, heuristic_type)
                        visualizer.reset_vehicle(start_node)
                        is_traveling = True
                        is_arrived = False
                        current_state = STATE_TRAVELLING

                # [1 / 2 / 3] Speed Multipliers
                elif event.key == pygame.K_1:
                    speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    speed_multiplier = 2.0
                elif event.key == pygame.K_3:
                    speed_multiplier = 4.0

        # -------------------------------------------------------------
        # 2. VEHICLE PHYSICS & PATH UPDATES
        # -------------------------------------------------------------
        if is_traveling and a_star_result and a_star_result.path:
            effective_speed = base_speed * speed_multiplier
            reached_end = visualizer.update_vehicle(a_star_result.path, speed=effective_speed)
            if reached_end:
                is_traveling = False
                is_arrived = True
                current_state = STATE_ARRIVED

        # -------------------------------------------------------------
        # 3. RENDERING PASS (CORRECT DRAWING LAYER ORDER)
        # -------------------------------------------------------------
        # Layer 1: Background & City Map (Roads, Buildings, Parks)
        visualizer.draw_city(city_map)

        # Layer 2: A* Search Frontier Ripple
        visualizer.draw_search_frontier(a_star_result)

        # Layer 3: Shortest Path & Dynamic Traveled Trail
        if a_star_result and a_star_result.path:
            visualizer.draw_path(a_star_result.path)

        # Layer 4: Start & Goal Beacon Markers
        visualizer.draw_endpoints(start_node, goal_node, pulse_tick)

        # Layer 5: Car Sprite, Dynamic Headlights & Exhaust Smoke
        if start_node is not None:
            visualizer.draw_vehicle()

        # Layer 6: Sidebar Dashboard & Telemetry HUD
        visualizer.draw_sidebar(
            state_text=current_state,
            start_node=start_node,
            goal_node=goal_node,
            a_star_result=a_star_result,
            heuristic_name=heuristic_type,
            speed_multiplier=speed_multiplier,
            is_traveling=is_traveling,
            is_arrived=is_arrived
        )

        # Swap Framebuffers
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
