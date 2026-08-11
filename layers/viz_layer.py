import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
import platform

# ========== 中文字体适配（核心修复点） ==========
# 自动适配不同系统的中文字体，Windows优先使用微软雅黑/黑体
system_name = platform.system()
if system_name == "Windows":
    # Windows系统常用中文字体列表，按优先级排序
    font_candidates = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]
elif system_name == "Darwin":  # macOS
    font_candidates = ["PingFang SC", "Heiti SC", "Arial Unicode MS"]
else:  # Linux
    font_candidates = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei"]

# 查找系统中实际存在的中文字体
available_fonts = [f.name for f in font_manager.fontManager.ttflist]
chinese_font = None
for font in font_candidates:
    if font in available_fonts:
        chinese_font = font
        break

# 应用字体配置
if chinese_font:
    plt.rcParams['font.sans-serif'] = [chinese_font]
else:
    # 兜底：如果没找到中文字体，强制加载系统字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']

# 解决负号显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False
# 统一设置绘图风格
sns.set_style("whitegrid", {"font.sans-serif": plt.rcParams['font.sans-serif']})


class Visualizer:
    def __init__(self):
        self.color_palette = sns.color_palette("Blues_d")

    def plot_missing_bar(self, missing_data):
        """缺失值分布柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="缺失占比(%)", y="字段名", data=missing_data, palette="Reds_d", ax=ax)
        ax.set_title("各字段缺失值占比分布", fontsize=14, pad=15)
        ax.set_xlabel("缺失占比(%)", fontsize=12)
        ax.set_ylabel("字段名称", fontsize=12)
        plt.tight_layout()
        return fig

    def plot_numeric_hist(self, data):
        """数值字段分布直方图"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        n_cols = 3
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten()

        for i, col in enumerate(numeric_cols):
            sns.histplot(data[col], kde=True, ax=axes[i], color="#2c7fb8")
            axes[i].set_title(f"{col} 分布", fontsize=12)
            axes[i].set_xlabel("")

        # 隐藏多余子图
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        return fig

    def plot_corr_heatmap(self, data):
        """参数相关性热力图"""
        numeric_data = data.select_dtypes(include=[np.number])
        corr = numeric_data.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax, square=True)
        ax.set_title("车辆参数相关性热力图", fontsize=14, pad=15)
        plt.tight_layout()
        return fig

    def plot_feature_weight(self, importance_data):
        """特征权重排序柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="权重值", y="特征名称", data=importance_data, palette="viridis", ax=ax)
        ax.set_title("价格影响因素权重排序", fontsize=14, pad=15)
        ax.set_xlabel("权重值", fontsize=12)
        ax.set_ylabel("特征名称", fontsize=12)
        plt.tight_layout()
        return fig

    def plot_price_compare(self, data, x_col):
        """价格-参数对比散点图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=x_col, y="厂商指导价(万)", data=data, s=100, color="#e34a33", ax=ax)
        ax.set_title(f"厂商指导价 vs {x_col}", fontsize=14, pad=15)
        plt.tight_layout()
        return fig

    def plot_pred_vs_true(self, y_true, y_pred):
        """实际售价与预测售价对比图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(y_true))
        ax.plot(x, y_true, marker='o', label="实际价格", linewidth=2)
        ax.plot(x, y_pred, marker='s', label="预测价格", linewidth=2, linestyle="--")
        ax.set_title("实际售价 vs 预测售价对比", fontsize=14, pad=15)
        ax.set_xlabel("样本序号", fontsize=12)
        ax.set_ylabel("厂商指导价(万)", fontsize=12)
        ax.legend()
        plt.tight_layout()
        return fig

    def plot_error_dist(self, errors):
        """模型误差分布折线图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.kdeplot(errors, fill=True, color="#756bb1", ax=ax)
        ax.axvline(x=0, color="red", linestyle="--")
        ax.set_title("模型预测误差分布", fontsize=14, pad=15)
        ax.set_xlabel("误差值(万元)", fontsize=12)
        plt.tight_layout()
        return fig

    def plot_ai_vs_manual_compare(self, ai_data, manual_data, metric="缺失值数量"):
        """AI处理与手动处理结果对比柱状图"""
        compare_df = pd.DataFrame({
            "处理方式": ["AI自动处理", "手动代码处理"],
            metric: [ai_data, manual_data]
        })
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x="处理方式", y=metric, data=compare_df, palette=["#3182bd", "#31a354"], ax=ax)
        ax.set_title(f"AI vs 手动处理 效果对比：{metric}", fontsize=14, pad=15)
        plt.tight_layout()
        return fig