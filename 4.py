def cls_m(y, p):
    tp = sum(1 for a, b in zip(y, p) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y, p) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y, p) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y, p) if a == 1 and b == 0)
    acc = (tp + tn) / len(y)
    pre = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    spe = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * pre * rec / (pre + rec) if pre + rec else 0.0
    bal = (rec + spe) / 2
    return tp, tn, fp, fn, acc, pre, rec, spe, f1, bal


def reg_m(y, p):
    r = [a - b for a, b in zip(y, p)]
    m = sum(y) / len(y)
    ss = sum((a - m) ** 2 for a in y)
    se = sum(v * v for v in r)
    mae = sum(abs(v) for v in r) / len(r)
    mse = se / len(r)
    rmse = mse ** 0.5
    r2 = 1 - se / ss if ss else 0.0
    return r, m, ss, se, mae, mse, rmse, r2


y = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
pr = [0.91, 0.62, 0.48, 0.35, 0.80, 0.55, 0.42, 0.30, 0.15, 0.05]
p05 = [1 if x >= 0.50 else 0 for x in pr]
p07 = [1 if x >= 0.70 else 0 for x in pr]
m05 = cls_m(y, p05)
m07 = cls_m(y, p07)

ya = [3, 5, 7, 9, 11]
pa = [2, 6, 8, 8, 12]
pb = [4, 4, 6, 10, 10]
ra = reg_m(ya, pa)
rb = reg_m(ya, pb)

print("Question 4: Metrics")
print()
print("A) th=0.50")
print("pred:", p05)
print(f"TP={m05[0]}, TN={m05[1]}, FP={m05[2]}, FN={m05[3]}")
print(f"acc={m05[4]:.3f}, pre={m05[5]:.3f}, rec={m05[6]:.3f}, f1={m05[8]:.3f}, spe={m05[7]:.3f}, bal={m05[9]:.3f}")
print()
print("A) th=0.70")
print("pred:", p07)
print(f"TP={m07[0]}, TN={m07[1]}, FP={m07[2]}, FN={m07[3]}")
print(f"acc={m07[4]:.3f}, pre={m07[5]:.3f}, rec={m07[6]:.3f}, f1={m07[8]:.3f}, spe={m07[7]:.3f}, bal={m07[9]:.3f}")
print("lower th=0.50 is better if FN is costly")
print()
print("B) regression")
print("A:", ra)
print("B:", rb)
print("tie on MAE/MSE/RMSE/R2 here")
print("acc can hide minority errors; R2 is not a class metric")