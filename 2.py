def dec(b): return int(b, 2)


def fit(b):
    x = dec(b)
    return 0 if x >= 12 else x * (15 - x)


def cx(a, b): return a[:2] + b[2:], b[:2] + a[2:]


def flip(b, i):
    i -= 1
    return b[:i] + ("1" if b[i] == "0" else "0") + b[i + 1:]


pop = ["0011", "0110", "1011", "1110"]
r = [0.08, 0.37, 0.62, 0.93]
f = [fit(x) for x in pop]
tot = sum(f)
p = [x / tot for x in f]
c = []
t = 0.0
for x in p:
    t += x
    c.append(t)

sel = []
for x in r:
    for b, m in zip(pop, c):
        if x <= m:
            sel.append(b)
            break

a, b, d, e = sel
k1, k2 = cx(a, b)
k3, k4 = cx(d, e)
k2 = flip(k2, 1)
k3 = flip(k3, 4)
kid = [k1, k2, k3, k4]
best = pop[f.index(max(f))]
nxt = [best] + kid[:3]

print("Question 2: Genetic Algorithm")
print()
print("chrom   x  ok  fit   prob   cum")
for ch, ft, prb, cum in zip(pop, f, p, c):
    n = dec(ch)
    ok = "Y" if n < 12 else "N"
    print(f"{ch:>4}  {n:>2}  {ok:>1}  {ft:>3}  {prb:>5.4f}  {cum:>5.4f}")

print()
print("sel:")
for x, ch in zip(r, sel):
    print(f"{x:.2f} -> {ch}")

print()
print("cross:")
print(f"{a} x {b} -> {k1}, {k2}")
print(f"{d} x {e} -> {k3}, {k4}")

print()
print("kids:")
for i, b in enumerate(kid, 1):
    print(f"{i}: {b}  x={dec(b)}  fit={fit(b)}")

print()
print("elitism:", best)
print("next:", nxt)
print()
print("best x under x < 12: 7 or 8, fit = 56")
print("zero fitness for infeasible rows can cut diversity fast")
