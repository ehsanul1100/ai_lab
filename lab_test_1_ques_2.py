import heapq
graph = {
    'S': ['A', 'B'],
    'A': ['C', 'G'],
    'B': ['D', 'E'],
    'C': ['G'],
    'D': ['G'],
    'E': ['G'],
    'G': [],
}

hueristics = {
    'S': 5,
    'A': 2,
    'B': 4,
    'C': 3,
    'D': 1,
    'E': 5,
    'G': 0
}
start_node = 'S'
goal_node = 'G'
path = []

priority_queue = []
heapq.heappush(priority_queue, (hueristics[start_node], start_node))
visited = set()

while priority_queue:
    current_hueristic, current_node = heapq.heappop(priority_queue)
    if current_node in visited:
        continue
    path.append(current_node)
    visited.add(current_node)
    if current_node == goal_node:
        print("Goal node reached:", current_node)
        break
    
    for neighbor in graph[current_node]:
        if neighbor not in visited:
            heapq.heappush(priority_queue, (hueristics[neighbor], neighbor))
print("Path to goal node:")
for node in path:
    if node == path[-1]:
        print(node)
    else:
        print(node, end=" -> ")