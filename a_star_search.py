import heapq

# ==========================================
# 1. Greedy Best-First Search Function
# ==========================================
def greedy_best_first(graph, heuristics, start, goal):
    print("\n--- Running Greedy Best-First Search ---")
    queue = []
    
    # (Compass_Guess, Current_Node)
    heapq.heappush(queue, (heuristics[start], start))
    visited = set()
    
    while queue:
        guess, current = heapq.heappop(queue)
        
        if current in visited:
            continue
            
        print(f"📍 Visiting: {current}")
        visited.add(current)
        
        if current == goal:
            print("🎉 Goal Reached!")
            return
            
        if current in graph:  # Node tar theke kono rasta ache kina check
            for neighbor, _ in graph[current].items(): # Cost ta bad dilam (_)
                if neighbor not in visited:
                    heapq.heappush(queue, (heuristics[neighbor], neighbor))
                    
    print("❌ Goal could not be found.")

# ==========================================
# 2. A* (A-Star) Search Function
# ==========================================
def a_star_search(graph, heuristics, start, goal):
    print("\n--- Running A* Search ---")
    queue = []
    
    # (Total_Guess, Steps_Taken, Current_Node)
    heapq.heappush(queue, (heuristics[start], 0, start))
    visited = set()
    
    while queue:
        total_guess, steps_taken, current = heapq.heappop(queue)
        
        if current in visited:
            continue
            
        print(f"📍 Visiting: {current}")
        visited.add(current)
        
        if current == goal:
            print("🎉 Goal Reached! Total Cost: ", steps_taken)
            return
            
        if current in graph: # Node tar theke kono rasta ache kina check
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_steps_taken = steps_taken + distance
                    new_total_guess = new_steps_taken + heuristics[neighbor]
                    heapq.heappush(queue, (new_total_guess, new_steps_taken, neighbor))
                    
    print("❌ Goal could not be found.")

# ==========================================
# 3. Input Neyar System
# ==========================================
def main():
    graph = {}
    heuristics = {}
    
    print("========== Graph Input ==========")
    edges = int(input("Total koto gulo rasta (edges) ache?: "))
    print("Rasta gulo likho evabe: Node1 Node2 Cost (jemon: Start A 2)")
    
    all_nodes = set()
    
    for i in range(edges):
        u, v, cost = input(f"Rasta {i+1}: ").split()
        cost = int(cost)
        
        # Graph e rasta toiri kora
        if u not in graph:
            graph[u] = {}
        # Jodi undirected ba two-way rasta dorkar hoy tahole nicher 2 line un-comment korbe
        # if v not in graph:
        #     graph[v] = {}
            
        graph[u][v] = cost
        # graph[v][u] = cost  # Two-way er jonno
        
        all_nodes.add(u)
        all_nodes.add(v)
        
    print("\n========== Heuristics (Compass Guess) Input ==========")
    for node in all_nodes:
        h_val = int(input(f"Node '{node}' er heuristic guess koto?: "))
        heuristics[node] = h_val
        
    print("\n========== Start & Goal ==========")
    start_node = input("Start node konta?: ")
    goal_node = input("Goal node konta?: ")
    
    # Run the Algorithms!
    greedy_best_first(graph, heuristics, start_node, goal_node)
    a_star_search(graph, heuristics, start_node, goal_node)

# Code ta eখান thekei run hobe
if __name__ == "__main__":
    main()