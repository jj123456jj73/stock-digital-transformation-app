import streamlit as st
import pandas as pd

# ---------------------- 数据加载（相对路径） ----------------------
@st.cache_data  # 缓存数据，优化加载速度
def load_data():
    try:
        # 读取仓库根目录下的data.xlsx（相对路径）
        df = pd.read_excel("data.xlsx")
        return df
    except FileNotFoundError:
        st.error("❌ 未找到data.xlsx文件，请确认该文件已上传至仓库根目录")
        return None
    except Exception as e:
        st.error(f"加载数据失败：{str(e)}")
        return None

# ---------------------- 页面布局与交互 ----------------------
def main():
    # 页面标题
    st.title("上市公司数字化转型数据展示平台")
    st.divider()  # 分隔线

    # 加载数据
    data = load_data()
    if data is None:
        st.stop()  # 数据加载失败则终止后续流程

    # 原始数据展示
    st.subheader("📊 原始数据概览")
    st.dataframe(data, use_container_width=True)
    st.write(f"数据规模：{data.shape[0]} 行 × {data.shape[1]} 列")

    # 按企业名称筛选功能（适配你的数据列名）
    st.subheader("🔍 按企业名称筛选")
    if "企业名称" in data.columns:
        company_list = sorted(data["企业名称"].unique())
        selected_company = st.selectbox(
            "选择目标企业",
            options=company_list,
            index=0
        )
        filtered_data = data[data["企业名称"] == selected_company]
        st.dataframe(filtered_data, use_container_width=True)
    else:
        st.warning("数据中未包含「企业名称」列，无法使用企业筛选功能")

    # 数据统计示例
    st.subheader("📈 基础统计信息")
    st.write("数值型字段统计：")
    st.dataframe(data.describe(), use_container_width=True)

if __name__ == "__main__":
    main()
