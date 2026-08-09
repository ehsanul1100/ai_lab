import heapq


def best_first_search(graph, start, goal):
    # Priority queue: (distance, node)
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}  # To reconstruct the path
    g_score = {start: 0}  # Cost to reach each node

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)

        if current_node == goal:
            # Reconstruct path
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            return path[::-1], g_score[goal]  # Return path and distance

        for neighbor, cost in graph[current_node]:
            tentative_g = g_score[current_node] + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g
                heapq.heappush(open_set, (tentative_g, neighbor))

    return None, None  # No path found


# Define a simple graph: {node: [(neighbor, cost), ...]}
graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('D', 2), ('C', 5)],
    'C': [('D', 1)],
    'D': []
}


# Run searches
start = 'A'
goal = 'C'

# Best-First Search (no heuristic)
path, distance = best_first_search(graph, start, goal)
print("Best-First Search Path:", path, "Distance:", distance)
