import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 页面基本配置
st.set_page_config(layout="wide", page_title="洪灏策略终端", page_icon="🛡️")
st_autorefresh(interval=60000, key="global_refresh")

# --- 2. 增强版 CSS (解决手机端黑底黑字及布局问题) ---
st.markdown("""
    <style>
    /* 核心卡片样式：自适应深色/浅色模式 */
    .stApp {
        background-attachment: fixed;
    }
    .modern-card {
        background-color: rgba(255, 255, 255, 0.05); /* 适配深色模式的半透明感 */
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    /* 强制调整标题和正文颜色，确保在深色背景下可见 */
    .card-title {
        color: #3b82f6; /* 蓝色标题 */
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 1rem;
    }
    /* 手机端字体微调 */
    @media (max-width: 768px) {
        .modern-card { padding: 1rem; }
        .metric-row { font-size: 0.9rem; }
    }
    /* 标签颜色 */
    .status-tag {
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 数据获取 (保持稳健) ---
@st.cache_data(ttl=60)
def get_data():
    try:
        intl = yf.download(["GC=F", "SI=F", "CL=F", "^VIX"], period="2d", interval="1d")['Close'].iloc[-1]
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_v = ak.fx_spot_quote()[lambda df: df['currency']=='USDCNH']['bid_close'].values[0]
        north = ak.stock_hsgt_north_cash_em(symbol="北向资金").iloc[-1]['当日成交净买入'] / 100
        return intl, sh_df['最新价'].values[0], sh_df['涨跌幅'].values[0], cnh_v, north
    except:
        return {"^VIX":15.8, "GC=F":2912, "SI=F":32.45, "CL=F":74.2}, 3382, 0.3, 6.9, 187

intl, sh_p, sh_d, cnh_v, north = get_data()

# --- 4. 标题部分 ---
st.title("🛡️ 洪灏策略 · 交易仪表盘")
st.caption(f"最后更新: {datetime.now().strftime('%H:%M:%S')} (实时刷新)")

# --- 5. 核心模块布局 ---
# 在手机端，columns 会自动纵向排列
c1, c2 = st.columns([1, 1])
c3, c4 = st.columns([1, 1])

with c1:
    st.markdown(f"""<div class="modern-card">
        <div class="card-title">🔭 市场全景雷达</div>
        <div class="metric-row"><span>上证指数</span><b style="color:#ff4b4b;">{sh_p} (+{sh_d}%)</b></div>
        <div class="metric-row"><span>离岸人民币</span><b>{cnh_v}</b> <span style="color:orange;">[观望]</span></div>
        <div class="metric-row"><span>实时金银比</span><b>{intl['GC=F']/intl['SI=F']:.1f}</b> <span style="color:#3b82f6;">[目标 44]</span></div>
        <div class="metric-row"><span>VIX 波动率</span><b>{intl['^VIX']:.1f}</b> <span style="color:#2ecc71;">[安全]</span></div>
        <div class="metric-row"><span>北向资金(周)</span><b>+{north:.0f}亿</b></div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<div class="modern-card">
        <div class="card-header card-title">📌 洪灏核心观点</div>
        <div class="metric-row"><span>美元信用衰减</span><span style="color:#2ecc71;">● 验证</span></div>
        <div class="metric-row"><span>大宗超级周期</span><span style="color:orange;">● 进行中</span></div>
        <div class="metric-row"><span>人民币升值</span><span style="color:orange;">● 等待</span></div>
        <div class="metric-row"><span>化工 vs 纳指</span><span style="color:#2ecc71;">● 负相关</span></div>
        <div class="metric-row"><span>美股顶部风险</span><span style="color:#2ecc71;">● 安全</span></div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown('<div class="modern-card"><div class="card-title">🔢 仓位 & 预测</div>', unsafe_allow_html=True)
    st.write(f"基础仓位：**60%**")
    st.progress(0.6)
    st.caption("2026 预测点位进度 (Q1-Q4)")
    st.progress(0.65)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown("""<div class="modern-card">
        <div class="card-title">📋 今日交易清单</div>
        <div class="metric-row"><b style="color:red;">[高]</b> <span>观察人民币 6.9 关口</span></div>
        <div class="metric-row"><b style="color:orange;">[中]</b> <span>分批建仓江西铜业</span></div>
        <div class="metric-row"><b style="color:#2ecc71;">[低]</b> <span>研究兴业矿业(金银比)</span></div>
    </div>""", unsafe_allow_html=True)

# --- 6. 核心资产跟踪 ---
st.markdown('<div class="modern-card"><div class="card-title">⭐ 核心资产跟踪</div>', unsafe_allow_html=True)
df = pd.DataFrame([
    {"标的": "化工ETF", "现价": 0.98, "止损": 0.90, "信号": "🔥圆弧底", "权重": "18%"},
    {"标的": "江西铜业", "现价": 24.8, "止损": 22.0, "信号": "⚖️铜金双驱", "权重": "14%"},
    {"标的": "兴业矿业", "现价": 17.2, "止损": 15.5, "信号": "🥈白银Beta", "权重": "12%"}
])
st.table(df) # 手机端 table 比 data_editor 更稳定，不会溢出
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. 底部监控 ---
st.markdown('<div class="modern-card" style="border-top: 4px solid #ff4b4b;"><div class="card-title">⚠️ 突发事件监控</div>', unsafe_allow_html=True)
m1, m2 = st.columns(2)
with m1:
    st.write("🔴 **特朗普关税**: 2月24日生效 · 出口压测")
    st.write("🟠 **沃什上任**: 美元>108 触发减仓")
with m2:
    st.write("🟠 **中东局势**: 布油 74.2 · 能源+5%")
    st.write("🟢 **白银支撑**: 现价支撑有效")
st.markdown('</div>', unsafe_allow_html=True)
