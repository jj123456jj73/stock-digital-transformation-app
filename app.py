import streamlit as st
import pandas as pd
import plotly.express as px
warnings.filterwarnings('ignore')

# 全局配置
st.set_page_config(
    page_title="企业数字化转型分析平台",
    page_icon="📊",
    layout="wide"
)

# 数据加载（容错优化）
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx", engine="openpyxl")
        # 列名清洗+空值处理
        df.columns = [col.strip() for col in df.columns]
        for col in ["企业名称", "股票代码"]:
            if col in df.columns:
                df[col] = df[col].fillna("未知").astype(str)
        # 数值列空值填充
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

# 可视化函数
def create_charts(df, filter_condition):
    # 筛选数据（兼容企业名称/股票代码）
    data = df.query(filter_condition) if filter_condition else df
    if data.empty:
        st.warning("无匹配数据")
        return
    
    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) < 1:
        st.warning("无数值数据可展示")
        return

    # 1. 指标柱状图
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 指标数值对比")
        avg_data = data[numeric_cols].mean().reset_index()
        avg_data.columns = ["指标", "数值"]
        fig_bar = px.bar(avg_data, x="指标", y="数值", title="企业数字化指标", color="指标")
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # 2. 雷达图
    with col2:
        st.subheader("📈 指标雷达分析")
        if len(numeric_cols) >= 3:
            radar_data = data[numeric_cols].mean().reset_index()
            radar_data.columns = ["指标", "数值"]
            fig_radar = px.line_polar(radar_data, r="数值", theta="指标", line_close=True)
            st.plotly_chart(fig_radar, use_container_width=True)

# 主页面
def main():
    st.title("企业数字化转型数据查询与分析平台")
    st.divider()

    df = load_data()
    if df is None:
        st.stop()

    # 左侧查询面板（新增股票代码查询）
    with st.sidebar:
        st.header("🔍 多维度查询")
        # 选择查询方式：企业名称/股票代码
        query_type = st.radio("查询方式", ["企业名称", "股票代码"], horizontal=True)
        
        # 企业名称查询
        if query_type == "企业名称" and "企业名称" in df.columns:
            company_list = sorted(df["企业名称"].unique())
            selected_company = st.selectbox("选择企业", company_list)
            filter_condition = f"`企业名称` == '{selected_company}'"
        
        # 股票代码查询
        elif query_type == "股票代码" and "股票代码" in df.columns:
            code_list = sorted(df["股票代码"].unique())
            selected_code = st.selectbox("选择股票代码", code_list)
            filter_condition = f"`股票代码` == '{selected_code}'"
        
        else:
            st.warning("数据中无对应查询字段")
            filter_condition = ""

        # 指标+年份筛选
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        selected_metrics = st.multiselect("选择关注指标", numeric_cols, default=numeric_cols[:3] if numeric_cols.size>=3 else numeric_cols)
        if "年份" in df.columns:
            year_list = sorted(df["年份"].dropna().unique())
            selected_year = st.select_slider("选择年份", year_list, value=year_list[0] if year_list else None)
            filter_condition += f" & `年份` == {selected_year}" if filter_condition else f"`年份` == {selected_year}"

    # 右侧数据展示
    if filter_condition:
        filtered_df = df.query(filter_condition)
        if not filtered_df.empty:
            st.subheader("📋 精准查询结果")
            # 展示选中字段
            display_cols = (["企业名称", "股票代码"] if all(c in df.columns for c in ["企业名称", "股票代码"]) else []) + selected_metrics + (["年份"] if "年份" in df.columns else [])
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            
            # 导出功能
            csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
            st.download_button("📥 导出结果", csv, f"{filtered_df.iloc[0][query_type] if filtered_df.iloc[0][query_type] else '数据'}.csv", "text/csv")

            # 可视化
            st.divider()
            create_charts(df, filter_condition)
        else:
            st.warning("无匹配数据")

if __name__ == "__main__":
    main()
