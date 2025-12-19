import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 固定Excel文件路径
FILE_PATH = r"C:\Users\nzqh_\Desktop\stock_app\data.xlsx"

# 页面基础配置
st.set_page_config(
    page_title="上市公司数字化转型查询",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载Excel数据
@st.cache_data(ttl=3600)
def load_excel_data():
    try:
        if not os.path.exists(FILE_PATH):
            st.error(f"❌ 未找到Excel文件！路径：{FILE_PATH}")
            st.stop()
        
        df = pd.read_excel(FILE_PATH, engine="openpyxl")
        df["股票代码"] = df["股票代码"].astype(str).str.replace(".0", "", regex=False)
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce").fillna(0).astype(int)
        df["数字化转型指数"] = pd.to_numeric(df["数字化转型指数"], errors="coerce").fillna(0)
        
        core_columns = ["股票代码", "企业名称", "年份", "数字化转型指数", 
                       "人工智能", "大数据", "云计算", "区块链", "物联网"]
        for col in core_columns:
            if col not in df.columns:
                df[col] = 0
        
        df = df[df["年份"] != 0].drop_duplicates(subset=["股票代码", "年份"])
        return df
    
    except Exception as e:
        st.error(f"❌ 数据加载失败！原因：{str(e)[:100]}")
        st.stop()

df = load_excel_data()

# ===================== 核心功能模块 =====================
st.title("📊 上市公司数字化转型指数查询系统")
st.markdown(f"### 数据范围：{df['年份'].min()}-{df['年份'].max()}年 | 覆盖公司：{df['企业名称'].nunique()}家")
st.markdown("---")

# 侧边栏查询条件
st.sidebar.header("🔍 查询条件")
query_keyword = st.sidebar.text_input(
    label="输入股票代码/企业名称",
    placeholder="示例：600000 或 浦发银行",
    value=""
)

# 单公司详细查询结果
st.subheader("一、单公司转型数据查询")
query_result = None  # 初始化查询结果
if query_keyword:
    query_result = df[
        (df["股票代码"].str.contains(query_keyword, na=False, case=False)) |
        (df["企业名称"].str.contains(query_keyword, na=False, case=False))
    ].sort_values("年份")
    
    if not query_result.empty:
        target_company = query_result["企业名称"].iloc[0]
        target_code = query_result["股票代码"].iloc[0]
        
        # 分栏展示：趋势图 + 详细数据
        col_chart, col_table = st.columns([3, 2])
        with col_chart:
            st.markdown(f"#### {target_company}（{target_code}）转型指数趋势")
            metrics = ["数字化转型指数", "人工智能", "大数据", "云计算", "区块链", "物联网"]
            selected_metric = st.selectbox("选择展示指标", metrics, index=0)
            
            fig = px.line(
                query_result,
                x="年份",
                y=selected_metric,
                height=350,
                template="plotly_white",
                color_discrete_sequence=["#2E86AB"]
            )
            fig.update_layout(
                xaxis_title="年份",
                yaxis_title=selected_metric,
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_table:
            st.markdown(f"#### {target_company}历年详细数据")
            display_columns = ["年份", "股票代码", "企业名称", "数字化转型指数", 
                             "人工智能", "大数据", "云计算", "区块链", "物联网"]
            st.dataframe(
                query_result[display_columns].reset_index(drop=True),
                hide_index=True,
                use_container_width=True
            )
    else:
        st.warning(f"⚠️ 未查询到包含「{query_keyword}」的公司数据")
else:
    st.info("💡 请在左侧输入股票代码或企业名称")

# 替换为：单公司细分词频对比图表（仅当查询到公司时显示）
if query_result is not None and not query_result.empty:
    st.markdown("---")
    st.subheader(f"二、{target_company}细分领域词频对比")
    
    # 提取该公司的细分词频数据（按年份聚合）
    segment_data = query_result.groupby("年份").agg({
        "人工智能": "mean",
        "大数据": "mean",
        "云计算": "mean",
        "区块链": "mean",
        "物联网": "mean"
    }).reset_index()
    
    # 转换为长格式，便于绘制多折线图
    segment_data_long = pd.melt(
        segment_data,
        id_vars=["年份"],
        value_vars=["人工智能", "大数据", "云计算", "区块链", "物联网"],
        var_name="细分领域",
        value_name="词频数"
    )
    
    # 绘制多折线对比图
    fig_segment = px.line(
        segment_data_long,
        x="年份",
        y="词频数",
        color="细分领域",
        height=400,
        template="plotly_white",
        title=f"{target_company}各细分领域词频变化趋势",
        color_discrete_sequence=["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
    )
    fig_segment.update_layout(
        xaxis_title="年份",
        yaxis_title="词频数",
        legend_title="细分领域",
        # 修复图例方向报错：将orientation改为"h"（小写）
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_segment, use_container_width=True)

# 数据统计卡片
st.markdown("---")
st.subheader("三、数据统计概览")
col1, col2, col3, col4 = st.columns(4)
col1.metric("覆盖年份总数", f"{df['年份'].nunique()}年")
col2.metric("总公司数量", f"{df['企业名称'].nunique()}家")
col3.metric("全市场平均转型指数", f"{df[df['数字化转型指数']>0]['数字化转型指数'].mean():.2f}")
col4.metric("最高转型指数", f"{df['数字化转型指数'].max():.2f}")