def relu(x): return x if x > 0 else 0.0


def fwd(x, w, b, v, c):
    z = w * x + b
    a = relu(z)
    y = v * a + c
    return z, a, y


def ls(y, yhat): return 0.5 * (y - yhat) ** 2


x = -1.0
y = -2 * x * x + x - 1
w = -1.0
b = 0.0
v = 1.0
c = 0.0
lr = 0.05

z, a, yhat = fwd(x, w, b, v, c)
L = ls(y, yhat)
d = yhat - y
dv = d * a
dc = d
dz = d * v if z > 0 else 0.0
dw = dz * x
db = dz

w2 = w - lr * dw
b2 = b - lr * db
v2 = v - lr * dv
c2 = c - lr * dc
z2, a2, y2 = fwd(x, w2, b2, v2, c2)
L2 = ls(y, y2)

x1 = 1.0
y1 = -2 * x1 * x1 + x1 - 1
z3, a3, y3 = fwd(x1, w, b, v, c)
L3 = ls(y1, y3)
d3 = y3 - y1
dv3 = d3 * a3
dc3 = d3
dz3 = d3 * v if z3 > 0 else 0.0
dw3 = dz3 * x1
db3 = dz3

print("Question 3: Neural Network Regression")
print()
print(f"x=-1 target y={y}")
print(f"before: z={z}, a={a}, yhat={yhat}, L={L}")
print(f"grads: dv={dv}, dc={dc}, dw={dw}, db={db}")
print(f"after: w={w2}, b={b2}, v={v2}, c={c2}")
print(f"recalc: z={z2}, a={a2}, yhat={y2}, L={L2}")
print()
print(f"x=1: z={z3}, a={a3}, yhat={y3}, y={y1}, L={L3}")
print(f"zero grads from ReLU off: dw={dw3}, db={db3}, dv={dv3}")
print(f"c grad still = {dc3}")
print()
print("one ReLU hidden unit gives a piecewise-linear model, so it cannot match the curved target exactly")
