import streamlit as st
import pandas as pd

# 读取Excel文件（已改为相对路径）
@st.cache_data  # 缓存数据，提升加载速度
def load_data():
    try:
        df = pd.read_excel("data.xlsx")  # 相对路径，对应仓库根目录的data.xlsx
        return df
    except FileNotFoundError:
        st.error("未找到data.xlsx文件，请确认文件已上传到仓库根目录")
        return None

# 页面标题
st.title("上市公司数字化转型数据展示")

# 加载并展示数据
data = load_data()
if data is not None:
    st.subheader("原始数据")
    st.dataframe(data, use_container_width=True)

    # 示例：简单的数据筛选
    st.subheader("按公司筛选")
    company = st.selectbox("选择公司", data["公司名称"].unique())
    filtered_data = data[data["公司名称"] == company]
    st.dataframe(filtered_data, use_container_width=True)

