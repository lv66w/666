import pandas as pd
import numpy as np
import re


class DataProcessor:
    def __init__(self):
        pass

    # ========== AI自动预处理逻辑（模拟AI工具输出） ==========
    def ai_preprocess(self, raw_data):
        """AI自动处理：缺失值填充、异常标记、发动机拆分、字段类型判别"""
        df = raw_data.copy()

        # 1. 缺失值智能填充：数值列用均值，文本列用众数
        for col in df.columns:
            if df[col].dtype in [np.float64, np.int64]:
                # 先转数值，再用均值填充
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[f"{col}_AI填充标记"] = df[col].isnull().map({True: "是", False: "否"})
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "未知")

        # 2. 异常值标记（3σ原则）
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df["AI异常标记"] = "正常"
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            if std == 0:
                continue
            outlier_mask = (df[col] < mean - 3 * std) | (df[col] > mean + 3 * std)
            df.loc[outlier_mask, "AI异常标记"] = "含异常值"

        # 3. 发动机字段拆分
        if "发动机" in df.columns:
            df[["排量", "最大马力", "气缸形式"]] = df["发动机"].apply(
                lambda x: pd.Series(self._split_engine(x))
            )

        return df

    # ========== 手动数据清洗工具 ==========
    def clean_data(self, data):
        """二次清洗：格式标准化、冗余字段剔除、数值转换"""
        df = data.copy()

        # 数值字段类型转换
        numeric_cols = ["厂商指导价", "最大功率(kw)", "最大扭矩(N-m)", "长度(mm)",
                        "宽度(mm)", "高度(mm)", "轴距(mm)", "最高车速(km/h)", "官方0-100km/h加速(s)"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 剔除全空冗余字段
        df = df.dropna(axis=1, how='all')

        # 价格单位统一（保留万元）
        if "厂商指导价" in df.columns:
            df["厂商指导价(万)"] = df["厂商指导价"].astype(float)

        return df

    def split_engine_manual(self, data):
        """手动正则拆分发动机字段（更精准）"""
        df = data.copy()

        def parse_engine(text):
            if pd.isna(text):
                return np.nan, np.nan, np.nan, np.nan
            # 提取排量
            displacement = re.findall(r'(\d+\.?\d*)[LT]', str(text))
            disp = float(displacement[0]) if displacement else np.nan
            # 提取马力
            power = re.findall(r'(\d+)马力', str(text))
            hp = int(power[0]) if power else np.nan
            # 提取气缸数
            cylinder = re.findall(r'L(\d)|V(\d)|H(\d)', str(text))
            cyl_num = int(cylinder[0][0]) if cylinder else np.nan
            # 进气形式
            turbo = "涡轮增压" if "T" in str(text) else "自然吸气"
            return disp, hp, cyl_num, turbo

        if "发动机" in df.columns:
            df[["排量(L)", "最大马力(Ps)", "气缸数", "进气形式"]] = df["发动机"].apply(
                lambda x: pd.Series(parse_engine(x))
            )
        return df

    def detect_outliers(self, data, method="iqr"):
        """异常值检测：IQR / 3σ"""
        df = data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_df = pd.DataFrame(index=df.index)

        for col in numeric_cols:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
            else:  # 3σ
                mean = df[col].mean()
                std = df[col].std()
                lower = mean - 3 * std
                upper = mean + 3 * std
            outlier_df[f"{col}_异常"] = (df[col] < lower) | (df[col] > upper)

        df["手动异常标记"] = outlier_df.any(axis=1).map({True: "异常", False: "正常"})
        return df

    def one_hot_encode(self, data, cols):
        """分类字段独热编码"""
        df = data.copy()
        for col in cols:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
        return df

    # ========== 内部辅助函数 ==========
    def _split_engine(self, text):
        """AI简化版发动机拆分"""
        if pd.isna(text):
            return np.nan, np.nan, "未知"
        parts = str(text).split()
        disp = parts[0] if len(parts) > 0 else np.nan
        hp = parts[1] if len(parts) > 1 else np.nan
        type_ = parts[-1] if len(parts) > 0 else "未知"
        return disp, hp, type_