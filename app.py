import streamlit as st
import pandas as pd
import sys
import os

# 路径配置
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from layers.data_layer import DataManager
from layers.utils_layer import DataProcessor
from layers.model_layer import PricePredictModel
from layers.viz_layer import Visualizer

# ===================== 全局UI样式配置 (核心美化部分) =====================
st.set_page_config(
    page_title="汽车大数据综合分析系统",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏默认的Streamlit菜单和页脚
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 自定义CSS
st.markdown("""
    <style>
    /* --- 全局字体与背景 --- */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
        color: #2d3748;
    }
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        min-height: 100vh;
    }

    /* --- 标题美化 --- */
    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 3px solid #4a5568;
        display: inline-block;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-title {
        font-size: 22px;
        font-weight: 700;
        color: #2b6cb0;
        margin-top: 30px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    .sub-title::before {
        content: '';
        display: inline-block;
        width: 6px;
        height: 24px;
        background: #4299e1;
        border-radius: 3px;
        margin-right: 10px;
    }

    /* --- 侧边栏美化 --- */
    [data-testid="stSidebar"] {
        background-color: #1a202c;
        background-image: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        border-bottom: 1px solid #4a5568;
    }
    .sidebar-title span {
        font-size: 32px;
        display: block;
        margin-bottom: 10px;
    }
    /* 侧边栏选项文字颜色 */
    .stRadio > label {
        color: #e2e8f0;
        font-weight: 500;
    }

    /* --- 卡片容器 --- */
    .info-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s;
    }
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }

    /* --- 按钮美化 --- */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        height: 45px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* 主按钮颜色 */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #3182ce 0%, #63b3ed 100%);
        color: white;
    }
    /* 次级按钮颜色 */
    div.stButton > button[kind="secondary"] {
        background: #ffffff;
        color: #4a5568;
        border: 1px solid #cbd5e0;
    }

    /* --- 指标卡片 (Metric) --- */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        color: #718096;
        font-size: 16px;
    }
    div[data-testid="stMetricValue"] {
        color: #2d3748;
        font-size: 28px;
        font-weight: 700;
    }

    /* --- 表格美化 --- */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ===================== 全局状态初始化 =====================
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()
if "processor" not in st.session_state:
    st.session_state.processor = DataProcessor()
if "model" not in st.session_state:
    st.session_state.model = PricePredictModel()
if "viz" not in st.session_state:
    st.session_state.viz = Visualizer()

dm = st.session_state.data_manager
processor = st.session_state.processor
model = st.session_state.model
viz = st.session_state.viz

# ===================== 侧边栏导航 =====================
with st.sidebar:
    st.markdown('<div class="sidebar-title"><span>🚗</span>汽车大数据分析系统</div>', unsafe_allow_html=True)

    page = st.radio(
        "功能导航",
        ["📊 数据概览", "🧹 数据处理", "📈 可视化分析", "🤖 智能价格预测", "⚖️ AI vs 手动对比"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("版本：V1.0 | 全流程数据分析平台")

# ===================== 页面1：数据概览 =====================
if page == "📊 数据概览":
    st.markdown('<p class="main-title">📊 数据源对接与概览</p>', unsafe_allow_html=True)

    # 上传区域
    upload_col, demo_col = st.columns([4, 1])
    with upload_col:
        uploaded_file = st.file_uploader("上传汽车对比Excel文件", type=["xlsx"], help="支持 .xlsx 格式文件")
    with demo_col:
        st.write("")  # 占位
        st.write("")
        use_demo = st.button("加载示例数据", type="secondary", use_container_width=True)

    # 加载数据逻辑
    if uploaded_file:
        status, msg = dm.load_raw_data(uploaded_file=uploaded_file)
        if status:
            st.success(msg)
        else:
            st.error(msg)

    if use_demo:
        demo_data = {
            "车型名称": ["宝马5系 2023款 530Li 领先型", "奔驰A级 2022款 A 180 L运动轿车", "科雷傲(进口) 2016款 2.5L",
                         "奥迪A7L 2023款 黑武士版", "捷豹E-PACE2024款进取运动版"],
            "厂商指导价": [47.55, 23.48, 27.88, 48.67, 28.80],
            "厂商": ["华晨宝马", "北京奔驰", "雷诺(进口)", "上汽奥迪", "奇瑞捷豹路虎"],
            "级别": ["中大型车", "紧凑型车", "紧凑型SUV", "中大型车", "紧凑型SUV"],
            "能源类型": ["汽油", "汽油", "汽油", "汽油", "汽油+48V轻混系统"],
            "最大功率(kw)": [180, 100, 126, 180, 147],
            "最大扭矩(N-m)": [350, 200, 225, 370, 280],
            "发动机": ["2.0T 245马力 L4", "1.3T 136马力 L4", "2.5L 171马力 L4", "2.0T 245马力 L4", "1.5T 200马力 L3"],
            "长度(mm)": [5106, 4622, 4522, 5076, 4395],
            "宽度(mm)": [1868, 1796, 1855, 1908, 1900],
            "高度(mm)": [1500, 1459, 1707, 1429, 1648],
            "轴距(mm)": [3105, 2789, 2690, 3026, 2681],
            "最高车速(km/h)": [250, 218, 181, 208, 210],
            "官方0-100km/h加速(s)": [7, 9, 10.3, None, 9.9],
            "前悬架类型": ["双叉臂式独立悬架", "麦弗逊式独立悬架", "麦弗逊式独立悬架", "五连杆独立悬架",
                           "麦弗逊式独立悬架"],
            "后悬架类型": ["多连杆式独立悬架", "扭力梁式非独立悬架", "多连杆式独立悬架", "五连杆独立悬架",
                           "多连杆式独立悬架"]
        }
        dm.raw_data = pd.DataFrame(demo_data)
        st.success("示例数据加载成功！")

    # 数据展示
    if dm.raw_data is not None:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">📌 数据核心指标</p>', unsafe_allow_html=True)
        info = dm.get_basic_info(dm.raw_data)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("数据行数", info["行数"], "款车型")
        col2.metric("字段列数", info["列数"], "项参数")
        col3.metric("缺失值总数", info["缺失值总数"])
        col4.metric("缺失值占比", f"{info['缺失值占比']}%")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<p class="sub-title">📋 原始数据预览</p>', unsafe_allow_html=True)
        st.dataframe(dm.raw_data, use_container_width=True, height=280)

        missing_df = dm.get_missing_stats(dm.raw_data)
        if not missing_df.empty:
            st.markdown('<p class="sub-title">🔍 缺失值一键筛查</p>', unsafe_allow_html=True)
            st.dataframe(missing_df, use_container_width=True, height=180)
        else:
            st.info("✅ 数据集无缺失值，数据质量良好")

# ===================== 页面2：数据处理 =====================
elif page == "🧹 数据处理":
    st.markdown('<p class="main-title">🧹 数据清洗与特征工程</p>', unsafe_allow_html=True)
    if dm.raw_data is None:
        st.warning("⚠️ 请先在「数据概览」页面加载数据")
    else:
        # AI预处理模块
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">第一步：AI自动预处理</p>', unsafe_allow_html=True)
        ai_col1, ai_col2 = st.columns([1, 5])
        with ai_col1:
            ai_run_btn = st.button("执行AI预处理", type="primary", use_container_width=True)
        with ai_col2:
            st.caption("自动完成：缺失值智能填充、异常值标记、发动机字段拆分、字段类型判别")

        if ai_run_btn:
            dm.ai_data = processor.ai_preprocess(dm.raw_data)
            st.success("✅ AI自动预处理执行完成")
            if dm.ai_data is not None:
                st.dataframe(dm.ai_data, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

        # 手动处理模块
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">第二步：手动代码深度处理</p>', unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        clean_btn = btn_col1.button("执行数据清洗", type="primary", use_container_width=True)
        split_btn = btn_col2.button("发动机字段拆分", use_container_width=True)
        outlier_btn = btn_col3.button("异常值检测", use_container_width=True)

        if clean_btn:
            dm.clean_data = processor.clean_data(dm.raw_data)
            st.success("✅ 数据清洗完成，数值格式已标准化、冗余字段已剔除")
        if split_btn:
            if dm.clean_data is None:
                dm.clean_data = processor.clean_data(dm.raw_data)
            dm.clean_data = processor.split_engine_manual(dm.clean_data)
            st.success("✅ 发动机字段精准拆分完成，已提取排量、马力、气缸数、进气形式")
        if outlier_btn:
            if dm.clean_data is None:
                dm.clean_data = processor.clean_data(dm.raw_data)
            dm.clean_data = processor.detect_outliers(dm.clean_data)
            st.success("✅ 异常值检测完成，已标记异常样本")

        if dm.clean_data is not None:
            st.dataframe(dm.clean_data, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

        # 导出按钮
        st.markdown("")
        export_col1, export_col2 = st.columns([4, 1])
        with export_col2:
            excel_bytes = dm.export_data(dm.clean_data)
            st.download_button(
                label="📥 导出处理结果",
                data=excel_bytes,
                file_name="清洗后汽车数据.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

# ===================== 页面3：可视化分析 =====================
elif page == "📈 可视化分析":
    st.markdown('<p class="main-title">📈 多维可视化分析</p>', unsafe_allow_html=True)
    if dm.clean_data is None:
        st.warning("⚠️ 请先在「数据处理」页面完成数据清洗")
    else:
        tab1, tab2, tab3, tab4 = st.tabs([" 分布分析 ", " 相关性分析 ", " 特征权重 ", " 价格对比 "])

        with tab1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">数值字段分布直方图</p>', unsafe_allow_html=True)
            fig_hist = viz.plot_numeric_hist(dm.clean_data)
            st.pyplot(fig_hist, use_container_width=True)

            missing_df = dm.get_missing_stats(dm.raw_data)
            if not missing_df.empty:
                st.markdown('<p class="sub-title">缺失值分布柱状图</p>', unsafe_allow_html=True)
                fig_miss = viz.plot_missing_bar(missing_df)
                st.pyplot(fig_miss, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">车辆参数相关性热力图</p>', unsafe_allow_html=True)
            fig_corr = viz.plot_corr_heatmap(dm.clean_data)
            st.pyplot(fig_corr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">价格影响因素权重排序</p>', unsafe_allow_html=True)
            if model.feature_importance is not None:
                fig_weight = viz.plot_feature_weight(model.feature_importance)
                st.pyplot(fig_weight, use_container_width=True)
            else:
                st.info("💡 请先在「智能价格预测」页面训练模型，生成特征权重")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">价格与参数对比分析</p>', unsafe_allow_html=True)
            numeric_cols = dm.clean_data.select_dtypes(include=['number']).columns.tolist()
            x_col = st.selectbox("选择对比参数", numeric_cols, index=0)
            fig_price = viz.plot_price_compare(dm.clean_data, x_col)
            st.pyplot(fig_price, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ===================== 页面4：智能价格预测 =====================
elif page == "🤖 智能价格预测":
    st.markdown('<p class="main-title">🤖 厂商指导价智能预测</p>', unsafe_allow_html=True)
    if dm.clean_data is None:
        st.warning("⚠️ 请先完成数据清洗")
    else:
        # 模型训练区
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">🔧 模型训练</p>', unsafe_allow_html=True)
        model_col1, model_col2 = st.columns([2, 1])
        with model_col1:
            model_type = st.selectbox("选择回归算法模型", ["随机森林回归", "线性回归"])
        with model_col2:
            st.write("")
            st.write("")
            train_btn = st.button("开始训练模型", type="primary", use_container_width=True)

        if train_btn:
            m_type = "random_forest" if model_type == "随机森林回归" else "linear"
            metrics, importance = model.train_model(dm.clean_data, model_type=m_type)
            st.success("✅ 模型训练完成！")

            # 评估指标卡片
            st.markdown('<p class="sub-title">📊 模型评估指标</p>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R² 得分", metrics["R²得分"], "拟合优度")
            col2.metric("平均绝对误差", f"{metrics['平均绝对误差(MAE)']} 万", "MAE")
            col3.metric("均方误差", metrics["均方误差(MSE)"], "MSE")
            col4.metric("均方根误差", f"{metrics['均方根误差(RMSE)']} 万", "RMSE")
        st.markdown('</div>', unsafe_allow_html=True)

        # 单样本预测
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">🎯 手动参数预测</p>', unsafe_allow_html=True)
        if model.model:
            col1, col2, col3 = st.columns(3)
            params = {}
            for i, col in enumerate(model.feature_cols):
                with [col1, col2, col3][i % 3]:
                    params[col] = st.number_input(col, value=float(dm.clean_data[col].mean()))

            pred_col1, pred_col2 = st.columns([4, 1])
            with pred_col2:
                predict_btn = st.button("预测价格", type="primary", use_container_width=True)

            if predict_btn:
                price, msg = model.predict_single(params)
                st.markdown(f"""
                                <div style="background:#ebf8ff; border-radius:8px; padding:20px; border-left:4px solid #2b6cb0; margin:10px 0;">
                                    <h3 style="color:#2c5282; margin:0;">预测厂商指导价：<span style="color:#e53e3e;">{price} 万元</span></h3>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("💡 请先点击上方按钮训练模型，再进行价格预测")
            st.markdown('</div>', unsafe_allow_html=True)

            # 模型效果可视化
            if model.model:
                st.markdown('<p class="sub-title">📉 模型效果可视化</p>', unsafe_allow_html=True)
                tab_pred1, tab_pred2 = st.tabs([" 实际值vs预测值对比 ", " 误差分布 "])
                with tab_pred1:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    fig_pred = viz.plot_pred_vs_true(model.y_true, model.y_pred)
                    st.pyplot(fig_pred, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with tab_pred2:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    errors = model.get_error_distribution()
                    fig_err = viz.plot_error_dist(errors)
                    st.pyplot(fig_err, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # ===================== 页面5：AI vs 手动对比 =====================
        elif page == "⚖️ AI vs 手动对比":
            st.markdown('<p class="main-title">⚖️ AI自动处理 vs 手动代码处理 效果对比</p>', unsafe_allow_html=True)
            if dm.ai_data is None or dm.clean_data is None:
                st.warning("⚠️ 请先完成AI预处理与手动处理，再查看对比结果")
            else:
                # 核心指标对比
                ai_missing = int(dm.ai_data.isnull().sum().sum())
                manual_missing = int(dm.clean_data.isnull().sum().sum())

                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("AI自动处理后缺失值数量", ai_missing, "均值/众数填充")
                with col2:
                    st.metric("手动代码处理后缺失值数量", manual_missing, "定制化策略填充")

                st.markdown('<p class="sub-title">📊 缺失值处理效果对比</p>', unsafe_allow_html=True)
                fig_compare = viz.plot_ai_vs_manual_compare(ai_missing, manual_missing, "缺失值数量")
                st.pyplot(fig_compare, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<p class="sub-title">📋 综合能力对比表</p>', unsafe_allow_html=True)
                compare_table = pd.DataFrame({
                    "对比维度": ["缺失值填充策略", "发动机字段拆分精度", "异常值检测方法", "字段格式标准化程度",
                                 "可定制化程度", "处理效率"],
                    "AI自动处理": ["均值/众数通用填充", "粗粒度拆分", "3σ原则", "基础格式转换", "低，固定规则",
                                   "高，一键完成"],
                    "手动代码处理": ["可自定义策略（中位数/固定值等）", "正则精准拆分，维度更细", "IQR/3σ 多方法可选",
                                     "深度标准化、单位统一", "高，可灵活调整规则", "中，需分步执行"]
                })
                st.table(compare_table)