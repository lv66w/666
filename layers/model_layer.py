import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler


class PricePredictModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = []
        self.metrics = {}
        self.feature_importance = None
        self.y_true = None
        self.y_pred = None

    def prepare_features(self, data):
        """特征工程：筛选建模特征、标准化处理"""
        df = data.copy()
        # 筛选数值型特征作为自变量
        numeric_cols = ["最大功率(kw)", "最大扭矩(N-m)", "长度(mm)", "宽度(mm)",
                        "高度(mm)", "轴距(mm)", "最高车速(km/h)", "排量(L)", "最大马力(Ps)"]
        # 只保留存在且无缺失的列
        valid_cols = [col for col in numeric_cols if col in df.columns and df[col].isnull().sum() == 0]
        self.feature_cols = valid_cols

        X = df[valid_cols].fillna(0)
        y = df["厂商指导价(万)"]
        return X, y

    def train_model(self, data, model_type="random_forest"):
        """训练回归模型，支持线性回归与随机森林"""
        X, y = self.prepare_features(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # 特征标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # 选择模型
        if model_type == "linear":
            self.model = LinearRegression()
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

        self.model.fit(X_train_scaled, y_train)
        y_pred = self.model.predict(X_test_scaled)

        # 保存评估指标
        self.metrics = {
            "R²得分": round(r2_score(y_test, y_pred), 4),
            "平均绝对误差(MAE)": round(mean_absolute_error(y_test, y_pred), 4),
            "均方误差(MSE)": round(mean_squared_error(y_test, y_pred), 4),
            "均方根误差(RMSE)": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)
        }

        # 保存真实值与预测值对比
        self.y_true = y_test.values
        self.y_pred = y_pred

        # 计算特征权重
        if model_type == "random_forest":
            importance = self.model.feature_importances_
        else:
            importance = np.abs(self.model.coef_)

        self.feature_importance = pd.DataFrame({
            "特征名称": self.feature_cols,
            "权重值": importance
        }).sort_values("权重值", ascending=False).reset_index(drop=True)

        return self.metrics, self.feature_importance

    def predict_single(self, params):
        """单样本价格预测：输入参数字典，输出预测价格"""
        if not self.model:
            return None, "模型未训练"

        # 按特征列顺序构造输入
        input_vec = []
        for col in self.feature_cols:
            input_vec.append(params.get(col, 0))

        input_scaled = self.scaler.transform([input_vec])
        pred_price = self.model.predict(input_scaled)[0]
        return round(pred_price, 2), "预测成功"

    def get_error_distribution(self):
        """获取误差分布数据"""
        errors = self.y_true - self.y_pred
        return errors