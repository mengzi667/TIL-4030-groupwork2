import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 读取数据
data = pd.read_csv('data/SanFrancisco/grid_with_bike_counts.csv')

# 分离特征和目标变量
X = data.drop(columns=['geometry', 'start_count', 'end_count'])
y_start = data['start_count']
y_end = data['end_count']

# 将数据分为训练集和测试集（针对 start_count）
X_train_start, X_test_start, y_train_start, y_test_start = train_test_split(X, y_start, test_size=0.2, random_state=42)

# 将数据分为训练集和测试集（针对 end_count）
X_train_end, X_test_end, y_train_end, y_test_end = train_test_split(X, y_end, test_size=0.2, random_state=42)

# 标准化数据
scaler = StandardScaler()
X_train_start = scaler.fit_transform(X_train_start)
X_test_start = scaler.transform(X_test_start)
X_train_end = scaler.fit_transform(X_train_end)
X_test_end = scaler.transform(X_test_end)

# 定义模型
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(random_state=42)
}

# 训练和评估模型
results = {}
for name, model in models.items():
    # 训练模型（start_count）
    model.fit(X_train_start, y_train_start)
    y_pred_start = model.predict(X_test_start)
    mse_start = mean_squared_error(y_test_start, y_pred_start)
    r2_start = r2_score(y_test_start, y_pred_start)

    # 训练模型（end_count）
    model.fit(X_train_end, y_train_end)
    y_pred_end = model.predict(X_test_end)
    mse_end = mean_squared_error(y_test_end, y_pred_end)
    r2_end = r2_score(y_test_end, y_pred_end)

    # 保存结果
    results[name] = {
        "start_count": {"MSE": mse_start, "R2": r2_start},
        "end_count": {"MSE": mse_end, "R2": r2_end}
    }

# 打印评估结果
print("Regression Model Comparison Results:")
for name, result in results.items():
    print(f"{name}:")
    print(f"  start_count - MSE: {result['start_count']['MSE']}, R2: {result['start_count']['R2']}")
    print(f"  end_count - MSE: {result['end_count']['MSE']}, R2: {result['end_count']['R2']}")

# 绘制所有模型的拟合图
for name, model in models.items():
    # 拟合图（start_count）
    model.fit(X_train_start, y_train_start)
    y_pred_start = model.predict(X_test_start)

    plt.figure(figsize=(12, 6))
    plt.scatter(y_test_start, y_pred_start, alpha=0.6, label='Predicted vs Actual')
    plt.plot([y_test_start.min(), y_test_start.max()], [y_test_start.min(), y_test_start.max()], 'r--', label='Ideal Fit')
    plt.xlabel('Actual start_count')
    plt.ylabel('Predicted start_count')
    plt.title(f'{name}: Actual vs Predicted (start_count)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # 拟合图（end_count）
    model.fit(X_train_end, y_train_end)
    y_pred_end = model.predict(X_test_end)

    plt.figure(figsize=(12, 6))
    plt.scatter(y_test_end, y_pred_end, alpha=0.6, label='Predicted vs Actual')
    plt.plot([y_test_end.min(), y_test_end.max()], [y_test_end.min(), y_test_end.max()], 'r--', label='Ideal Fit')
    plt.xlabel('Actual end_count')
    plt.ylabel('Predicted end_count')
    plt.title(f'{name}: Actual vs Predicted (end_count)')
    plt.legend()
    plt.grid(True)
    plt.show()

# 确定最优模型（以 R2 分数为准）
best_model_name = max(results, key=lambda name: results[name]['start_count']['R2'] + results[name]['end_count']['R2'])
best_model = models[best_model_name]

# 进行敏感性分析，展示各要素重要程度（仅适用于树模型）
if hasattr(best_model, 'feature_importances_'):
    best_model.fit(X_train_start, y_train_start)  # 重新训练最优模型
    feature_importances = best_model.feature_importances_
    features = X.columns

    # 绘制特征重要性图
    plt.figure(figsize=(12, 6))
    plt.barh(features, feature_importances, align='center')
    plt.xlabel('Feature Importance')
    plt.title(f'Feature Importance in {best_model_name}')
    plt.show()
else:
    print(f"The best model ({best_model_name}) does not support feature importances.")