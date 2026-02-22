import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 页面配置与美化 (还原图片质感)
st.set_page_config(layout="wide", page_title="洪灏策略·交易仪表盘")
st_autorefresh(interval=60000, key="global_refresh")

# 自定义 CSS：复刻图片中的卡片圆角、背景色和字体
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: white; padding: 15px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card { background-color: white; padding: 20px; border-radius: 20px; border: 1px solid #e6e9ef; height: 100%; }
    .status-tag { padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: bold; }
    .section-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据抓取 (实时关联图片指标) ---
@st.cache_data(ttl=50)
def get_full_data():
    intl = yf.download(["GC=F", "SI=F", "CL=F", "^VIX"], period="2d", interval="1d")['Close'].iloc[-1]
    try:
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh = ak.fx_spot_quote()
        cnh_v = cnh[cnh['currency'] == 'USDCNH']['bid_close'].values[0]
        sh_v = sh_df['最新价'].values[0]
        sh_delta = sh_df['涨跌幅'].values[0]
    except: sh_v, sh_delta, cnh_v = 3382, 0.3, 6.9
    return intl, sh_v, sh_delta, cnh_v

intl_p, sh_p, sh_d, cnh_p = get_full_data()

# --- 3. 顶部标题栏 ---
t1, t2 = st.columns([3, 1])
with t1: st.header("洪灏策略 · 交易仪表盘")
with t2: st.write(f"最后更新: {datetime.now().strftime('%H:%M:%S')}")

# --- 4. 第一排：四个核心模块 (对应图片第一行) ---
col1, col2, col3, col4 = st.columns(4)

with col1: # 市场全景雷达
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔭 市场全景雷达 <span style="font-size:10px; color:gray; margin-left:10px;">实时</span></div>', unsafe_allow_html=True)
    st.metric("上证指数", f"{sh_p}", f"{sh_d}%")
    st.metric("离岸人民币 (CNH)", f"{cnh_p}", "观望")
    st.metric("黄金 / 白银", f"{intl_p['GC=F']:.0f} / {intl_p['SI=F']:.2f}")
    gs_r = intl_p['GC=F']/intl_p['SI=F']
    st.metric("金银比", f"{gs_r:.1f}", "目标: 44", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with col2: # 洪灏核心观点
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📌 洪灏核心观点</div>', unsafe_allow_html=True)
    views = [("美元信用衰减", "🟢 验证"), ("大宗超级周期", "🟡 进行中"), ("人民币升值", "🟡 等待"), ("金银比回归44", "🟡 空间较大")]
    for v, s in views:
        st.write(f"{v} : **{s}**")
    st.markdown('</div>', unsafe_allow_html=True)

with col3: # 仓位计算器 & 2026预测
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔢 仓位计算器</div>', unsafe_allow_html=True)
    st.write("**基础仓位: 60%**")
    st.markdown('<div class="section-title">📅 2026 预测日历</div>', unsafe_allow_html=True)
    qs = {"Q1 (3200-3600)": 0.65, "Q2 (3400-3800)": 0.45, "Q3 (3600-4000)": 0.2}
    for k, v in qs.items():
        st.write(f"{k}")
        st.progress(v)
    st.markdown('</div>', unsafe_allow_html=True)

with col4: # 今日交易清单
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 今日交易清单</div>', unsafe_allow_html=True)
    st.info("🔴 高: 观察人民币是否站稳6.90")
    st.warning("🟠 中: 准备分批建仓江西铜业")
    st.success("🟢 低: 研究兴业矿业")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 第二排：核心资产跟踪 (自选池) ---
st.markdown("---")
st.markdown('<div class="section-title">⭐ 核心资产跟踪 <span style="font-size:12px; background:#eef; padding:2px 8px; border-radius:10px; margin-left:10px;">自选池</span></div>', unsafe_allow_html=True)

# 动态持仓表 (复刻图片表头和内容)
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "目标": 1.20, "止损": 0.90, "权重": 0.18},
        {"标的": "工商银行", "代码": "601398", "目标": 7.00, "止损": 5.70, "权重": 0.22},
        {"标的": "江西铜业", "代码": "600362", "目标": 32.0, "止损": 22.0, "权重": 0.14},
        {"标的": "科大讯飞", "代码": "002230", "目标": 65.0, "止损": 45.0, "权重": 0.12}
    ])

# 允许编辑
edited_df = st.data_editor(st.session_state.assets, num_rows="dynamic", use_container_width=True)

# 渲染实时计算
stocks_real = ak.stock_zh_a_spot_em()
final_table = []
for _, r in edited_df.iterrows():
    m = stocks_real[stocks_real['代码'] == str(r['代码']).zfill(6)]
    if not m.empty:
        curr = m['最新价'].values[0]
        final_table.append({
            "标的": r['标的'], "现价": curr, "目标": r['目标'], "止损": r['止损'],
            "信号": "🔥 底部" if curr > r['止损'] else "⚠️ 破位",
            "权重": f"{r['权重']*100:.0f}%"
        })
st.table(pd.DataFrame(final_table))

# --- 6. 第三排：突发事件监控 (底部横幅) ---
st.markdown('<div class="card" style="border-left: 5px solid #ff4b4b;">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚠️ 突发事件监控</div>', unsafe_allow_html=True)
e1, e2, e3 = st.columns(3)
e1.write("🔴 **特朗普15%关税**\n\n2月24日生效，出口承压")
e2.write("🟠 **中东局势**\n\n布油 74.2，触发能源+5%")
e3.write("🟢 **白银支撑有效**\n\n2月8日 · 现价 32.45")
st.markdown('</div>', unsafe_allow_html=True)
