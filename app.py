import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ---------------------- 全局配置 ----------------------
st.set_page_config(
    page_title="企业数字化转型分析平台",
    page_icon="📊",
    layout="wide"  # 宽屏布局
)

# ---------------------- 数据加载（容错优化） ----------------------
@st.cache_data
def load_data():
    try:
        # 读取Excel（相对路径，兼容xlsx/xls）
        df = pd.read_excel("data.xlsx", engine="openpyxl")
        
        # 数据清洗：统一列名格式+处理空值
        df.columns = [col.strip() for col in df.columns]  # 去除列名空格
        if "企业名称" in df.columns:
            df["企业名称"] = df["企业名称"].fillna("未知企业").astype(str)
        
        # 处理数值列空值
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        return df
    except FileNotFoundError:
        st.error("❌ 未找到data.xlsx文件，请确认文件已上传至仓库根目录")
        return None
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

# ---------------------- 可视化图表函数 ----------------------
def create_charts(df, selected_company):
    # 筛选该企业数据
    company_data = df[df["企业名称"] == selected_company]
    if company_data.empty:
        st.warning("该企业无数据可展示")
        return
    
    # 提取数值列（排除非数值字段）
    numeric_cols = company_data.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) < 1:
        st.warning("无数值型数据生成图表")
        return
    
    # 1. 柱状图：企业各维度指标
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 企业各维度指标对比")
        # 取该企业第一条数据（若有多行取均值）
        company_values = company_data[numeric_cols].mean().reset_index()
        company_values.columns = ["指标", "数值"]
        
        fig_bar = px.bar(
            company_values,
            x="指标",
            y="数值",
            title=f"{selected_company} 数字化转型指标",
            color="指标",
            width=500,
            height=400
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 2. 雷达图：企业指标雷达分析（需至少3个数值列）
    with col2:
        st.subheader("📈 企业指标雷达图")
        if len(numeric_cols) >= 3:
            radar_data = company_data[numeric_cols].mean().reset_index()
            radar_data.columns = ["指标", "数值"]
            
            fig_radar = px.line_polar(
                radar_data,
                r="数值",
                theta="指标",
                line_close=True,
                title=f"{selected_company} 指标雷达分析",
                width=500,
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("需至少3个数值型指标生成雷达图")
    
    # 3. 行业对比（若有行业列）
    st.subheader("🏢 同行业指标对比")
    if "行业" in df.columns:
        df["行业"] = df["行业"].fillna("未知行业")
        industry = company_data["行业"].iloc[0]
        industry_data = df[df["行业"] == industry]
        
        # 行业均值对比
        industry_mean = industry_data[numeric_cols].mean().reset_index()
        industry_mean.columns = ["指标", "行业均值"]
        company_mean = company_data[numeric_cols].mean().reset_index()
        company_mean.columns = ["指标", "企业值"]
        
        compare_data = pd.merge(industry_mean, company_mean, on="指标")
        fig_compare = px.bar(
            compare_data,
            x="指标",
            y=["行业均值", "企业值"],
            barmode="group",
            title=f"{industry} - {selected_company} 行业对比",
            width=800,
            height=400
        )
        st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------- 主页面逻辑 ----------------------
def main():
    st.title("企业数字化转型数据查询与分析平台")
    st.divider()

    # 加载数据
    df = load_data()
    if df is None:
        st.stop()

    # 左侧查询面板
    with st.sidebar:
        st.header("🔍 高级查询")
        
        # 1. 企业名称筛选
        company_list = sorted(df["企业名称"].unique())
        selected_company = st.selectbox(
            "选择企业",
            options=company_list,
            index=0
        )
        
        # 2. 指标筛选（可选）
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        selected_metrics = st.multiselect(
            "选择关注指标",
            options=numeric_cols,
            default=numeric_cols[:3] if len(numeric_cols)>=3 else numeric_cols
        )
        
        # 3. 数据范围筛选（若有年份列）
        if "年份" in df.columns:
            year_list = sorted(df["年份"].dropna().unique())
            selected_year = st.select_slider(
                "选择年份",
                options=year_list,
                value=year_list[0] if year_list else None
            )
            df = df[df["年份"] == selected_year]

    # 右侧数据展示
    col_left, col_right = st.columns([2, 1])
    
    # 左侧：查询结果
    with col_left:
        st.subheader("📋 精准查询结果")
        # 筛选数据
        filtered_df = df[df["企业名称"] == selected_company]
        # 展示选中的指标
        if selected_metrics:
            filtered_df = filtered_df[["企业名称"] + selected_metrics + ([col for col in ["行业", "年份"] if col in df.columns])]
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        # 数据导出
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出查询结果",
            data=csv,
            file_name=f"{selected_company}_数字化转型数据.csv",
            mime="text/csv"
        )
    
    # 右侧：企业基础信息
    with col_right:
        st.subheader("ℹ️ 企业基础信息")
        company_info = df[df["企业名称"] == selected_company].iloc[0]
        st.write(f"企业名称：{company_info['企业名称']}")
        if "行业" in df.columns:
            st.write(f"所属行业：{company_info['行业']}")
        if "年份" in df.columns:
            st.write(f"数据年份：{company_info['年份']}")
        st.write(f"有效指标数：{len(numeric_cols)}")
        st.write(f"数据行数：{len(filtered_df)}")

    # 可视化图表区域
    st.divider()
    create_charts(df, selected_company)

if __name__ == "__main__":
    main()
