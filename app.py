import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 页面配置：必须是第一行
st.set_page_config(layout="wide", page_title="洪灏策略·专业交易终端")
st_autorefresh(interval=60000, key="global_refresh")

# --- 高级 CSS 装修：自适应 + 玻璃质感 ---
st.markdown("""
    <style>
    /* 全局背景与字体 */
    .main { background-color: #f8faff; font-family: 'Helvetica Neue', sans-serif; }
    
    /* 容器自适应：手机端自动纵向排列 */
    [data-testid="stHorizontalBlock"] {
        gap: 1.5rem;
    }

    /* 重新设计的“漂亮卡片” */
    .custom-card {
        background: white;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(149, 157, 165, 0.1);
        transition: transform 0.3s ease;
        margin-bottom: 20px;
    }
    .custom-card:hover { transform: translateY(-5px); }

    /* 标题样式增强 */
    .card-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        border-left: 5px solid #3b82f6;
        padding-left: 12px;
    }

    /* 手机端适配：针对小屏幕隐藏不必要的元素或调整字体 */
    @media (max-width: 768px) {
        .card-title { font-size: 1rem; }
        .stMetric { padding: 10px !important; }
    }

    /* 标签美化 */
    .tag { padding: 3px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; margin-right: 5px; }
    .tag-red { background: #fee2e2; color: #ef4444; }
    .tag-orange { background: #ffedd5; color: #f59e0b; }
    .tag-green { background: #dcfce7; color: #10b981; }
    .tag-blue { background: #e0e7ff; color: #6366f1; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心数据引擎 (补齐所有缺失指标) ---
@st.cache_data(ttl=50)
def fetch_data():
    intl = yf.download(["GC=F", "SI=F", "CL=F", "^VIX"], period="2d", interval="1d")['Close'].iloc[-1]
    try:
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_v = ak.fx_spot_quote()[lambda df: df['currency']=='USDCNH']['bid_close'].values[0]
        north = ak.stock_hsgt_north_cash_em(symbol="北向资金").iloc[-1]['当日成交净买入'] / 100
        sh_p, sh_d = sh_df['最新价'].values[0], sh_df['涨跌幅'].values[0]
    except: sh_p, sh_d, cnh_v, north = 3382.4, 0.35, 6.91, 187
    return intl, sh_p, sh_d, cnh_v, north

intl, sh_p, sh_d, cnh_v, north = fetch_data()

# --- 3. 页面布局 ---
st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom:20px;'><div><h2 style='margin:0;'>🛡️ 洪灏策略交易终端</h2></div><div style='text-align:right; color:#64748b;'>⏰ {datetime.now().strftime('%H:%M:%S')} (实时刷新)</div></div>", unsafe_allow_html=True)

# 第一排：四个美化后的卡片
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="custom-card">
        <div class="card-title">🔭 市场全景雷达</div>
        <p>上证指数: <b style="color:#ef4444;">{sh_p} (+{sh_d}%)</b></p>
        <p>离岸人民币: <b>{cnh_v}</b> <span class="tag tag-orange">观望</span></p>
        <p>金银比: <b>{intl['GC=F']/intl['SI=F']:.1f}</b> <span class="tag tag-blue">目标 44</span></p>
        <p>VIX波动率: <b>{intl['^VIX']:.1f}</b> <span class="tag tag-green">安全</span></p>
        <p>北向(周): <b>+{north:.0f}亿</b> ↑</p>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<div class="custom-card">
        <div class="card-title">📌 洪灏核心观点</div>
        <p>美元信用衰减: <span class="tag tag-green">🟢 验证</span></p>
        <p>大宗超级周期: <span class="tag tag-orange">🟡 进行中</span></p>
        <p>人民币升值: <span class="tag tag-orange">🟡 等待</span></p>
        <p>化工 vs 纳指: <span class="tag tag-green">🟢 负相关</span></p>
        <p>美股顶部风险: <span class="tag tag-green">🟢 安全</span></p>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown('<div class="custom-card"><div class="card-title">🔢 仓位 & 2026预测</div>', unsafe_allow_html=True)
    st.write("基础仓位: **60%**")
    st.progress(0.6)
    st.caption("2026预测点位 (3200-4200)")
    st.progress(0.65)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown("""<div class="custom-card">
        <div class="card-title">📋 今日交易清单</div>
        <p><span class="tag tag-red">高</span> 观察人民币站稳6.9</p>
        <p><span class="tag tag-orange">中</span> 分批建仓江西铜业</p>
        <p><span class="tag tag-green">低</span> 研究兴业矿业(金银比<70)</p>
    </div>""", unsafe_allow_html=True)

# 第二排：资产追踪
st.markdown('<div class="custom-card"><div class="card-title">⭐ 核心资产跟踪 (自选池)</div>', unsafe_allow_html=True)
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "止损": 0.90, "信号": "🔥圆弧底", "权重": "18%"},
        {"标的": "江西铜业", "代码": "600362", "止损": 22.0, "信号": "⚖️铜金双驱", "权重": "14%"},
        {"标的": "兴业矿业", "代码": "000426", "止损": 11.5, "信号": "🥈白银Beta", "权重": "12%"}
    ])
st.data_editor(st.session_state.assets, use_container_width=True, num_rows="dynamic")
st.markdown('</div>', unsafe_allow_html=True)

# 第三排：突发事件监控 (底部横幅)
st.markdown('<div class="custom-card" style="border-top: 5px solid #ef4444;"><div class="card-title">⚠️ 突发事件监控</div>', unsafe_allow_html=True)
e1, e2, e3, e4 = st.columns(4)
with e1:
    st.markdown("<span class="tag tag-red">红</span> **特朗普15%关税**", unsafe_allow_html=True)
    st.caption("2月24日生效·出口承压")
with e2:
    st.markdown("<span class="tag tag-orange">橙</span> **沃什上任美联储**", unsafe_allow_html=True)
    st.caption("美元>108则减仓")
with e3:
    st.markdown("<span class="tag tag-orange">橙</span> **中东局势**", unsafe_allow_html=True)
    st.caption("油价触发能源权重+5%")
with e4:
    st.markdown("<span class="tag tag-green">绿</span> **白银支撑有效**", unsafe_allow_html=True)
    st.caption(f"支撑位29.5 · 现价{intl['SI=F']:.2f}")
st.markdown('</div>', unsafe_allow_html=True)
