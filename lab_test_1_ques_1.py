x = [1, 2, 3, 4, 5]
y = [52, 57, 61, 68, 72]
b1, b0 = 0, 0
mean_x = 0
mean_y = 0
for i in range(len(x)):
    mean_x += x[i]
    mean_y += y[i]
mean_x /= len(x)
mean_y /= len(y)
sum_xy = 0
sum_x = 0
for i in range(len(x)):
    sum_xy += (x[i] - mean_x) * (y[i] - mean_y)
    sum_x += (x[i] - mean_x) ** 2
b1 = sum_xy / sum_x if sum_x != 0 else 0
b0 = mean_y - b1 * mean_x
c = 0.2
y_pred = []
for i in range(len(x)):
    y_pred.append(b0 + b1 * x[i] + c)
residual = []
for i in range(len(y)):
    residual.append(y[i] - y_pred[i])
rmse = 0.0
for i in range(len(residual)):
    rmse += residual[i] ** 2
rmse = (rmse / len(residual)) ** 0.5
r_squared = 0.0
sum_y_y_pred = 0.0
sum_y_mean = 0.0
for i in range(len(y)):
    sum_y_y_pred += (y[i] - y_pred[i]) ** 2
    sum_y_mean += (y[i] - mean_y) ** 2
r_squared = 1 - (sum_y_y_pred / sum_y_mean) if sum_y_mean != 0 else 0
print("Constants 'c':", c)
print("Slope (b1):", b1)
print("Intercept (b0):", b0)
print("Predicted y values:", y_pred)
print("Residuals:", residual)
print("RMSE:", rmse)
print("R-squared:", r_squared)