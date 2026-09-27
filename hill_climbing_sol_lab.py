from typing import List,Tuple
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
def fnc(x: int) -> int:
    return -(x**2) + 10*x + 5
def cal_nxt_st(x: int) -> Tuple[int, int]:
    xlft = x - 1
    xrgt = x + 1
    flft = fnc(xlft)
    frgt = fnc(xrgt)
    if flft > frgt:
        return xlft, flft
    else:
        return xrgt, frgt
        
x = 2
crv: List[Tuple[int, int]] = []
while True:
    if x >10 or x < 0:
        break
    crv.append((x, fnc(x)))
    nxt_x, fnxt_x = cal_nxt_st(x)
    if fnxt_x < fnc(x):
        break
    x = nxt_x

fig, ax = plt.subplots(figsize=(8, 5))
x_vals = np.linspace(0, 10, 200)
ax.plot(x_vals, fnc(x_vals), 'b-', label=r'$f(x) = -x^2 + 10x + 5$')
ax.grid(True, alpha=0.3)
point, = ax.plot([], [], 'ro', markersize=10, label='Current State')
path_line, = ax.plot([], [], 'r--', alpha=0.6, label='Visited Path')
status_text = ax.text(0.05, 0.90, '', transform=ax.transAxes, fontsize=11,
                      bbox=dict(boxstyle="round", fc="w", ec="0.5"))
def init():
    point.set_data([], [])
    path_line.set_data([], [])
    status_text.set_text('')
    return point, path_line, status_text
def update(frame):
    xs = [s[0] for s in crv[:frame+1]]
    ys = [s[1] for s in crv[:frame+1]]
    point.set_data([crv[frame][0]], [crv[frame][1]])
    path_line.set_data(xs, ys)
    status_text.set_text(f"Step {frame}: x={crv[frame][0]}, f(x)={crv[frame][1]}\ncrv: {crv[:frame+1]}")
    return point, path_line, status_text
ani = animation.FuncAnimation(fig, update, frames=len(crv), init_func=init, interval=800, repeat=True)
plt.title("Hill Climbing Live Graph")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.legend(loc='upper right')
plt.show()
