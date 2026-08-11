import pandas as pd
import numpy as np
from io import BytesIO


class DataManager:
    def __init__(self):
        self.raw_data = None  # 原始结构化数据（行=车型，列=参数）
        self.ai_data = None  # AI预处理后数据
        self.clean_data = None  # 手动清洗后数据

    def load_raw_data(self, file_path=None, uploaded_file=None):
        """
        加载原始对比表Excel，自动适配「参数在行、车型在列」的结构
        自动转置为标准结构化表：行=车型，列=特征
        """
        try:
            # 1. 读取原始Excel，不预设索引
            if uploaded_file:
                df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=0)
            elif file_path:
                df_raw = pd.read_excel(file_path, sheet_name=0, header=0)
            else:
                return False, "未传入数据文件"

            # 2. 处理前两列复合表头：第0列是大类，第1列是具体参数名
            # 提取参数名列表（用第1列作为参数名，去除空值）
            param_names = df_raw.iloc[:, 1].fillna("").tolist()

            # 3. 提取车型列：从第2列开始都是车型数据
            car_cols = df_raw.columns[2:].tolist()

            # 4. 提取每个车型对应的参数值，构造结构化表
            data_list = []
            for car in car_cols:
                # 跳过空列名/NaN列名
                if pd.isna(car) or str(car).strip() == "":
                    continue
                row_data = {"车型名称": car}
                for idx, param in enumerate(param_names):
                    if param.strip() == "":
                        continue
                    # 参数名去重处理，避免重复参数名
                    param_clean = param.strip()
                    if param_clean in row_data:
                        param_clean = f"{param_clean}_{idx}"
                    row_data[param_clean] = df_raw.loc[idx, car]
                data_list.append(row_data)

            # 5. 转为DataFrame，去除全空列
            self.raw_data = pd.DataFrame(data_list)
            self.raw_data = self.raw_data.dropna(axis=1, how='all')

            # 6. 价格字段预处理：去除"万"字，转为数值（提前处理方便后续分析）
            if "厂商指导价" in self.raw_data.columns:
                self.raw_data["厂商指导价"] = self.raw_data["厂商指导价"].astype(str).str.replace("万", "").str.strip()
                self.raw_data["厂商指导价"] = pd.to_numeric(self.raw_data["厂商指导价"], errors="coerce")

            return True, f"数据加载成功，共{self.raw_data.shape[0]}款车型，{self.raw_data.shape[1]}项参数"

        except Exception as e:
            return False, f"数据加载失败：{str(e)}"

    def get_basic_info(self, data):
        """获取数据集基础统计信息"""
        info = {
            "行数": data.shape[0],
            "列数": data.shape[1],
            "缺失值总数": int(data.isnull().sum().sum()),
            "缺失值占比": round(data.isnull().sum().sum() / (data.shape[0] * data.shape[1]) * 100, 2),
            "数值型字段数": len(data.select_dtypes(include=[np.number]).columns),
            "文本型字段数": len(data.select_dtypes(include=['object']).columns)
        }
        return info

    def get_missing_stats(self, data):
        """统计各字段缺失值详情"""
        missing = data.isnull().sum().reset_index()
        missing.columns = ["字段名", "缺失数量"]
        missing["缺失占比(%)"] = round(missing["缺失数量"] / len(data) * 100, 2)
        missing = missing[missing["缺失数量"] > 0].sort_values("缺失数量", ascending=False).reset_index(drop=True)
        return missing

    def export_data(self, data, file_name="processed_data.xlsx"):
        """导出数据为Excel文件"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name="处理结果")
        return output.getvalue()