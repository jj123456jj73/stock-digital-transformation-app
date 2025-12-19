import streamlit as st
import pandas as pd
import plotly.express as px

# 全局配置
st.set_page_config(
    page_title="企业数字化转型分析平台",
    page_icon="📊",
    layout="wide"
)

# 数据加载（强容错版）
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx", engine="openpyxl")
        # 1. 列名标准化
        df.columns = [col.strip().replace(" ", "_") for col in df.columns]
        # 2. 关键字段类型强制转换
        for col in ["企业名称", "股票代码"]:
            if col in df.columns:
                df[col] = df[col].fillna("未知").astype(str)
        # 3. 数值列统一转float（避免类型混乱）
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'object']).columns
        for col in numeric_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            except:
                pass
        return df
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

# 可视化函数（简化版）
def create_charts(data):
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) < 1:
        st.warning("无有效数值数据")
        return

    # 单栏柱状图（避免布局冲突）
    st.subheader("📊 企业数字化指标")
    avg_data = data[numeric_cols].mean().reset_index()
    avg_data.columns = ["指标", "数值"]
    fig = px.bar(avg_data, x="指标", y="数值", color="指标", height=400)
    st.plotly_chart(fig, use_container_width=True)

# 主页面（极简稳定版）
def main():
    st.title("企业数字化转型数据查询平台")
    st.divider()

    df = load_data()
    if df is None:
        st.stop()

    # 左侧查询面板（仅保留核心功能）
    with st.sidebar:
        st.header("🔍 查询条件")
        # 1. 企业名称/股票代码二选一
        query_col = st.selectbox("查询字段", ["企业名称", "股票代码"] if all(c in df.columns for c in ["企业名称", "股票代码"]) else ["企业名称"])
        # 2. 选项列表
        query_list = sorted(df[query_col].unique())
        selected_key = st.selectbox(f"选择{query_col}", query_list)
        # 3. 年份筛选（可选）
        year_filter = st.slider("选择年份", int(df["年份"].min()), int(df["年份"].max()), int(df["年份"].min())) if "年份" in df.columns else None

    # 数据筛选（极简逻辑）
    filtered_df = df[df[query_col] == selected_key]
    if year_filter:
        filtered_df = filtered_df[filtered_df["年份"] == year_filter]

    # 结果展示（避免复杂字段组合）
    if not filtered_df.empty:
        st.subheader("📋 查询结果")
        # 仅展示前10列（避免字段过多导致转换错误）
        display_df = filtered_df.iloc[:, :10]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # 可视化
        st.divider()
        create_charts(filtered_df)
    else:
        st.warning("无匹配数据")

if __name__ == "__main__":
    main()
