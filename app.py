import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------- 基础配置 ----------------------
st.set_page_config(
    page_title="企业数据查询与可视化平台",
    page_icon="📊",
    layout="wide"
)

# ---------------------- 数据加载（终极容错版） ----------------------
@st.cache_data
def load_data():
    try:
        # 读取Excel并强制指定引擎
        df = pd.read_excel("data.xlsx", engine="openpyxl")
        # 1. 列名标准化（去除空格/特殊字符）
        df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]
        # 2. 关键字段处理
        for col in ["企业名称", "股票代码"]:
            if col in df.columns:
                df[col] = df[col].fillna("未知").astype(str)
        # 3. 数值列清洗（仅保留可计算的数值）
        numeric_cols = []
        for col in df.columns:
            if col not in ["企业名称", "股票代码", "年份", "行业"]:
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                    numeric_cols.append(col)
                except:
                    pass
        # 4. 保留有效列
        keep_cols = ["企业名称", "股票代码"] + numeric_cols
        keep_cols = [col for col in keep_cols if col in df.columns]
        df = df[keep_cols]
        return df, numeric_cols
    except FileNotFoundError:
        st.error("❌ 未找到data.xlsx文件，请确认文件已上传到仓库根目录！")
        return None, []
    except Exception as e:
        st.error(f"⚠️ 数据加载出错：{str(e)}")
        return None, []

# ---------------------- 图表生成函数 ----------------------
def generate_charts(filtered_df, numeric_cols, query_value, query_type):
    if filtered_df.empty or len(numeric_cols) == 0:
        st.warning("⚠️ 无足够数据生成图表")
        return
    
    # 取该企业的均值（兼容多行数据）
    avg_data = filtered_df[numeric_cols].mean().reset_index()
    avg_data.columns = ["指标", "数值"]
    avg_data = avg_data[avg_data["数值"] > 0]  # 过滤0值指标
    
    if avg_data.empty:
        st.warning("⚠️ 无有效数值指标生成图表")
        return

    # 分栏展示图表
    col1, col2 = st.columns(2)
    
    # 1. 柱状图（核心指标对比）
    with col1:
        st.subheader("📊 核心指标数值")
        fig_bar = px.bar(
            avg_data,
            x="指标",
            y="数值",
            title=f"{query_value} 指标对比",
            color="指标",
            height=400
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 2. 饼图（指标占比）
    with col2:
        st.subheader("🥧 指标占比分布")
        fig_pie = px.pie(
            avg_data,
            values="数值",
            names="指标",
            title=f"{query_value} 指标占比",
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------- 主逻辑 ----------------------
def main():
    st.title("📈 企业数字化转型查询与可视化平台")
    st.divider()

    # 加载数据
    df, numeric_cols = load_data()
    if df is None:
        st.stop()

    # 左侧查询面板
    with st.sidebar:
        st.header("🔍 查询条件")
        
        # 选择查询维度
        query_options = []
        if "企业名称" in df.columns:
            query_options.append("企业名称")
        if "股票代码" in df.columns:
            query_options.append("股票代码")
        
        if not query_options:
            st.warning("❌ 数据中无「企业名称」或「股票代码」列！")
            st.stop()
        
        selected_query_type = st.radio("查询维度", query_options, horizontal=True)
        
        # 加载查询选项列表
        if selected_query_type == "企业名称":
            select_list = sorted(df["企业名称"].unique())
        else:
            select_list = sorted(df["股票代码"].unique())
        
        # 选择具体查询值
        selected_value = st.selectbox(f"选择{selected_query_type}", select_list, index=0)

    # 数据筛选
    filtered_df = df[df[selected_query_type] == selected_value]

    # 结果展示区
    col_left, col_right = st.columns([1, 2])
    
    # 左侧：企业基础信息
    with col_left:
        st.subheader("ℹ️ 企业基础信息")
        st.write(f"📌 {selected_query_type}：{selected_value}")
        st.write(f"📊 有效指标数：{len(numeric_cols)}")
        st.write(f"📥 数据行数：{len(filtered_df)}")
        
        # 导出功能
        csv_data = filtered_df.to_csv(index=False, encoding="utf-8")
        st.download_button(
            label="💾 导出数据",
            data=csv_data,
            file_name=f"{selected_value}_数据.csv",
            mime="text/csv"
        )
    
    # 右侧：查询结果表格
    with col_right:
        st.subheader("📋 详细数据")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # 图表展示区
    st.divider()
    generate_charts(filtered_df, numeric_cols, selected_value, selected_query_type)

# ---------------------- 运行入口 ----------------------
if __name__ == "__main__":
    main()
