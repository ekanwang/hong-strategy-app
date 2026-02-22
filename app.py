import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 页面配置与刷新
st.set_page_config(layout="wide", page_title="洪灏策略·专业交易终端", page_icon="🛡️")
st_autorefresh(interval=60000, key="global_refresh")

# --- 2. 深度定制 CSS (美化 + 手机适配) ---
st.markdown("""
    <style>
    /* 全局背景 */
    .main { background-color: #f8f9fc; }
    
    /* 响应式卡片：手机端自动纵向，电脑端横向 */
    .dashboard-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(149, 157, 165, 0.1);
        margin-bottom: 20px;
        border: none;
    }
    
    /* 标题美化 */
    .card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 手机端适配：当屏幕小于 768px 时调整 */
    @media (max-width: 768px) {
        .dashboard-card { padding: 15px; }
        .card-header { font-size: 1.2rem; }
        p { font-size: 1rem; }
    }

    /* 信号标签 */
    .tag { padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; }
    .tag-red { background: #ff4b4b; }
    .tag-orange { background: #ffa500; }
    .tag-green { background: #2ecc71; }
    .tag-blue { background: #3498db; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 数据抓取引擎 ---
@st.cache_data(ttl=60)
def get_market_data():
    try:
        intl = yf.download(["GC=F", "SI=F", "CL=F", "^VIX"], period="2d", interval="1d")['Close'].iloc[-1]
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_v = ak.fx_spot_quote()[lambda df: df['currency']=='USDCNH']['bid_close'].values[0]
        north = ak.stock_hsgt_north_cash_em(symbol="北向资金").iloc[-1]['当日成交净买入'] / 100
        return intl, sh_df['最新价'].values[0], sh_df['涨跌幅'].values[0], cnh_v, north
    except:
        return {"^VIX":19.0, "GC=F":2900, "SI=F":32.5, "CL=F":74.2}, 3382, 0.35, 6.91, 187

intl, sh_p, sh_d, cnh_v, north = get_market_data()

# --- 4. 顶部标题栏 ---
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: flex-end; padding: 10px 0;'>
        <h2 style='margin:0;'>🛡️ 洪灏策略 · 交易仪表盘</h2>
        <p style='color:#64748b; margin:0;'>⏰ {datetime.now().strftime('%H:%M:%S')} (实时刷新)</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 第一排：四个核心功能块 ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="dashboard-card">
        <div class="card-header">🔭 市场全景雷达</div>
        <p>上证指数: <b style="color:#ff4b4b;">{sh_p} (+{sh_d}%)</b></p>
        <p>离岸人民币: <b>{cnh_v}</b> <span class="tag tag-orange">观望</span></p>
        <p>金银比: <b>{intl['GC=F']/intl['SI=F']:.1f}</b> <span class="tag tag-blue">目标 44</span></p>
        <p>VIX波动率: <b>{intl['^VIX']:.1f}</b> <span class="tag tag-green">安全</span></p>
        <p>北向(周): <b>+{north:.0f}亿</b> ↑</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""<div class="dashboard-card">
        <div class="card-header">📌 洪灏核心观点</div>
        <p>美元信用衰减: <b style="color:#2ecc71;">● 验证</b></p>
        <p>大宗超级周期: <b style="color:#ffa500;">● 进行中</b></p>
        <p>人民币升值: <b style="color:#ffa500;">● 等待</b></p>
        <p>化工 vs 纳指: <b style="color:#2ecc71;">● 负相关</b></p>
        <p>金银比回归44: <b style="color:#ffa500;">● 空间较大</b></p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="dashboard-card"><div class="card-header">🔢 仓位 & 预测</div>', unsafe_allow_html=True)
    st.write("基础仓位: **60%**")
    st.progress(0.6)
    st.caption("2026预测进度 (Q1-Q4)")
    st.progress(0.65)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown("""<div class="dashboard-card">
        <div class="card-header">📋 今日交易清单</div>
        <p><span class="tag tag-red">高</span> 观察人民币站稳6.9</p>
        <p><span class="tag tag-orange">中</span> 分批建仓江西铜业</p>
        <p><span class="tag tag-green">低</span> 研究兴业矿业</p>
    </div>""", unsafe_allow_html=True)

# --- 6. 第二排：核心资产跟踪 ---
st.markdown('<div class="dashboard-card"><div class="card-header">⭐ 核心资产跟踪</div>', unsafe_allow_html=True)
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "现价": 0.98, "止损": 0.90, "信号": "🔥圆弧底", "权重": "18%"},
        {"标的": "江西铜业", "代码": "600362", "现价": 24.8, "止损": 22.0, "信号": "⚖️铜金双驱", "权重": "14%"},
        {"标的": "工商银行", "代码": "601398", "现价": 6.12, "止损": 5.70, "信号": "💰股息6.2%", "权重": "22%"}
    ])
st.data_editor(st.session_state.assets, use_container_width=True, num_rows="dynamic")
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. 第三排：突发事件监控 ---
st.markdown('<div class="dashboard-card" style="border-top: 5px solid #ff4b4b;"><div class="card-header">⚠️ 突发事件监控</div>', unsafe_allow_html=True)
e1, e2, e3, e4 = st.columns(4)
with e1:
    st.markdown("<span class='tag tag-red'>红</span> **特朗普15%关税**", unsafe_allow_html=True)
    st.caption("2月24日生效·出口承压")
with e2:
    st.markdown("<span class='tag tag-orange'>橙</span> **沃什上任美联储**", unsafe_allow_html=True)
    st.caption("美元>108则减仓")
with e3:
    st.markdown("<span class='tag tag-orange'>橙</span> **中东局势**", unsafe_allow_html=True)
    st.caption("布油 74.2 · 触发则能源+5%")
with e4:
    st.markdown("<span class='tag tag-green'>绿</span> **白银支撑有效**", unsafe_allow_html=True)
    st.caption(f"支撑有效 · 现价 {intl['SI=F']:.2f}")
st.markdown('</div>', unsafe_allow_html=True)
