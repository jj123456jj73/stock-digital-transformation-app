# 核心依赖导入（仅保留必要库）
import streamlit as st
import pandas as pd

# ---------------------- 页面基础配置 ----------------------
st.set_page_config(
    page_title="企业数字化转型查询平台",
    page_icon="📊",
    layout="centered",  # 居中布局，适配所有屏幕
    initial_sidebar_state="expanded"
)

# ---------------------- 数据加载（强容错） ----------------------
@st.cache_data  # 缓存数据，提升加载速度
def load_excel_data():
    """读取Excel文件，处理空值和格式问题"""
    try:
        # 读取仓库根目录的data.xlsx（相对路径）
        df = pd.read_excel("data.xlsx")
        
        # 1. 清洗列名（去除空格/特殊字符）
        df.columns = [str(col).strip() for col in df.columns]
        
        # 2. 处理关键字段空值
        if "企业名称" in df.columns:
            df["企业名称"] = df["企业名称"].fillna("未知企业").astype(str)
        if "股票代码" in df.columns:
            df["股票代码"] = df["股票代码"].fillna("未知代码").astype(str)
        
        # 3. 数值列空值填充（避免计算报错）
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        return df
    except FileNotFoundError:
        st.error("❌ 未找到data.xlsx文件，请确认文件已上传到仓库根目录！")
        return None
    except Exception as e:
        st.error(f"⚠️ 数据加载出错：{str(e)}")
        return None

# ---------------------- 主查询逻辑 ----------------------
def main():
    # 页面标题
    st.title("📈 企业数字化转型数据查询系统")
    st.divider()

    # 加载数据
    data_df = load_excel_data()
    if data_df is None:
        st.stop()  # 数据加载失败则终止

    # 左侧查询面板
    with st.sidebar:
        st.header("🔍 查询条件")
        
        # 选择查询方式（自动适配数据列）
        query_options = []
        if "企业名称" in data_df.columns:
            query_options.append("企业名称")
        if "股票代码" in data_df.columns:
            query_options.append("股票代码")
        
        if not query_options:
            st.warning("数据中无「企业名称」或「股票代码」列，无法查询！")
            st.stop()
        
        # 选择查询维度
        selected_query_type = st.radio(
            "查询维度",
            options=query_options,
            horizontal=True
        )

        # 根据选择的维度展示可选列表
        if selected_query_type == "企业名称":
            select_list = sorted(data_df["企业名称"].unique())
        else:  # 股票代码
            select_list = sorted(data_df["股票代码"].unique())
        
        # 选择具体查询值
        selected_value = st.selectbox(
            f"选择{selected_query_type}",
            options=select_list,
            index=0
        )

    # 数据筛选
    filtered_data = data_df[data_df[selected_query_type] == selected_value]

    # 展示查询结果
    st.subheader(f"📋 {selected_query_type}：{selected_value}")
    if not filtered_data.empty:
        # 展示筛选后的数据（隐藏索引，适配页面宽度）
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )
        # 数据导出功能
        csv_data = filtered_data.to_csv(index=False, encoding="utf-8")
        st.download_button(
            label="💾 导出查询结果（CSV）",
            data=csv_data,
            file_name=f"{selected_value}_数据.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ 未查询到该条件下的数据！")

# ---------------------- 运行入口 ----------------------
if __name__ == "__main__":
    main()
