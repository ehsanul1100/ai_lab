gph = {
    "S": [("A", 4), ("B", 1)],
    "A": [("C", 2), ("G", 9)],
    "B": [("A", 1), ("C", 5)],
    "C": [("G", 4)],
    "G": [],
}

h = {"S": 8, "A": 5, "B": 7, "C": 3, "G": 0}


def key(a):
    return min(range(len(a)), key=lambda i: (a[i][1] + a[i][2], a[i][0]))


def show(t, a):
    if a:
        print(t + ": " + " | ".join(f"{n}(g={g}, h={hh}, f={g + hh}, p={p or '-'})" for n, g, hh, p in sorted(a, key=lambda x: (x[1] + x[2], x[0]))))
    else:
        print(t + ": empty")


op = [["S", 0, h["S"], None]]
cl = []
g = {"S": 0}
par = {"S": None}

print("Question 1: A* Search - Better Path to a Node")
print("List version only, no extra graph class.\n")
show("OPEN", op)
show("CLOSED", cl)

st = 0
while op:
    i = key(op)
    n, c, hh, p = op.pop(i)
    cl.append([n, c, hh, p])

    print(f"\nStep {st}: expand {n}")
    print(f"Chosen node = {n}(g={c}, h={hh}, f={c + hh}, p={p or '-'})")

    for nx, w in gph[n]:
        if any(r[0] == nx for r in cl):
            continue
        ng = c + w
        j = next((k for k, r in enumerate(op) if r[0] == nx), -1)
        if j == -1:
            op.append([nx, ng, h[nx], n])
            par[nx] = n
            g[nx] = ng
            print(f"  gen {nx}(g={ng}, h={h[nx]}, f={ng + h[nx]}, p={n})")
        elif ng < op[j][1]:
            op[j] = [nx, ng, h[nx], n]
            par[nx] = n
            g[nx] = ng
            print(f"  better {nx}: g -> {ng}, p -> {n}")

    show("OPEN", op)
    show("CLOSED", cl)
    if n == "G":
        break
    st += 1

p = []
n = "G"
while n is not None:
    p.append(n)
    n = par[n]

print("\nFinal path:", " -> ".join(reversed(p)))
print("Final cost:", g["G"])
print("\nWhy A* needs both g(n) and h(n):")
print("g(n) is real cost so far; h(n) is the estimate to the goal.")
print("Using only h(n) can miss cheap paths, and using only g(n) ignores the goal.")