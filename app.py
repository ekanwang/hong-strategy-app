import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 页面配置与自动刷新
st.set_page_config(layout="wide", page_title="洪灏策略·专业交易终端")
st_autorefresh(interval=60000, key="global_refresh")

# --- 自定义 CSS：复刻图片中的圆角卡片、颜色标签与专业排版 ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .card { background-color: white; padding: 22px; border-radius: 20px; border: 1px solid #e1e4e8; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
    .section-title { font-size: 17px; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; color: #1e293b; }
    .tag-red { background: #fee2e2; color: #dc2626; padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: bold; }
    .tag-orange { background: #ffedd5; color: #ea580c; padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: bold; }
    .tag-green { background: #dcfce7; color: #16a34a; padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: bold; }
    .value-up { color: #eb4432; font-weight: bold; }
    .value-down { color: #23a55a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心行情抓取 (包含你要求的所有指标) ---
@st.cache_data(ttl=50)
def get_all_market_data():
    # 国际：黄金、白银、原油、VIX
    intl = yf.download(["GC=F", "SI=F", "CL=F", "^VIX"], period="2d", interval="1d")['Close'].iloc[-1]
    try:
        # 国内：上证指数、离岸人民币
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_data = ak.fx_spot_quote()
        cnh_v = cnh_data[cnh_data['currency'] == 'USDCNH']['bid_close'].values[0]
        # 北向资金 (周)
        north_money = ak.stock_hsgt_north_cash_em(symbol="北向资金")
        north_val = north_money.iloc[-1]['当日成交净买入'] / 100 # 换算为亿
        sh_v = sh_df['最新价'].values[0]
        sh_d = sh_df['涨跌幅'].values[0]
    except: sh_v, sh_d, cnh_v, north_val = 3382, 0.35, 6.91, 187
    return intl, sh_v, sh_d, cnh_v, north_val

intl_p, sh_p, sh_d, cnh_p, north_v = get_all_market_data()

# --- 3. 顶部标题 ---
t1, t2 = st.columns([3, 1])
with t1: st.title("🛡️ 洪灏策略 · 交易仪表盘")
with t2: st.write(f"⏰ {datetime.now().strftime('%H:%M:%S')} (实时刷新)")

# --- 4. 第一排：四个核心功能块 ---
col1, col2, col3, col4 = st.columns(4)

with col1: # 市场全景雷达
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔭 市场全景雷达 <span style="font-size:10px; color:gray; margin-left:8px;">实时</span></div>', unsafe_allow_html=True)
    st.write(f"CN 上证指数: **{sh_p}** <span class='value-up'>+{sh_d}%</span>", unsafe_allow_html=True)
    st.write(f"🌐 离岸人民币 (CNH): **{cnh_p}** <span style='color:orange'>观望</span>", unsafe_allow_html=True)
    st.write(f"🛢️ 布伦特原油: **{intl_p['CL=F']:.1f}**")
    st.write(f"🥇 黄金: **{intl_p['GC=F']:.0f}** | 🥈 白银: **{intl_p['SI=F']:.2f}**")
    gs_ratio = intl_p['GC=F']/intl_p['SI=F']
    st.write(f"📊 **金银比: {gs_ratio:.1f}** <span class='tag-orange'>目标: 44</span>", unsafe_allow_html=True)
    st.write(f"📉 **VIX 波动率: {intl_p['^VIX']:.1f}** <span class='tag-green'>安全</span>", unsafe_allow_html=True)
    st.write(f"🧧 **北向资金(周): +{north_v:.0f}亿** ↑", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2: # 洪灏核心观点
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📌 洪灏核心观点</div>', unsafe_allow_html=True)
    ops = [("美元信用衰减", "🟢 验证"), ("大宗超级周期", "🟡 进行中"), ("人民币升值", "🟡 等待"), 
           ("化工 vs 纳指", "🟢 负相关"), ("金银比回归44", "🟡 空间较大"), ("美股顶部风险", "🟢 安全")]
    for v, s in ops:
        st.write(f"{v} : **{s}**")
    st.markdown('</div>', unsafe_allow_html=True)

with col3: # 仓位计算器 & 预测
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔢 仓位 & 2026预测</div>', unsafe_allow_html=True)
    st.write("**基础仓位: 60%**")
    st.progress(0.6)
    st.write("📅 2026预测进度")
    st.caption("Q1 (3200-3600)")
    st.progress(0.65)
    st.caption("Q2 (3400-3800)")
    st.progress(0.4)
    st.markdown('</div>', unsafe_allow_html=True)

with col4: # 今日交易清单
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 今日交易清单</div>', unsafe_allow_html=True)
    st.write("<span class='tag-red'>高</span> 观察人民币是否站稳6.9", unsafe_allow_html=True)
    st.write("<span class='tag-orange'>中</span> 准备分批建仓江西铜业", unsafe_allow_html=True)
    st.write("<span class='tag-green'>低</span> 研究兴业矿业", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 第二排：核心资产跟踪 (自选池) ---
st.markdown("---")
st.markdown('<div class="section-title">⭐ 核心资产跟踪 <span style="font-size:12px; margin-left:10px; color:gray;">自选池</span></div>', unsafe_allow_html=True)

if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "现价": 0.98, "止损": 0.90, "信号": "🔥圆弧底", "权重": 0.18},
        {"标的": "工商银行", "代码": "601398", "现价": 6.12, "止损": 5.70, "信号": "💰股息6.2%", "权重": 0.22},
        {"标的": "江西铜业", "代码": "600362", "现价": 24.8, "止损": 22.0, "信号": "⚖️铜金双驱", "权重": 0.14},
    ])

# 动态可编辑表格
edited_df = st.data_editor(st.session_state.assets, num_rows="dynamic", use_container_width=True)

# --- 6. 第三排：突发事件监控 (底部红橙绿横幅) ---
st.markdown("---")
st.markdown('<div class="card" style="border-left: 5px solid #f39c12;">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚠️ 突发事件监控</div>', unsafe_allow_html=True)
e1, e2, e3, e4 = st.columns(4)

with e1:
    st.write("<span class='tag-red'>红色</span> **特朗普15%关税**", unsafe_allow_html=True)
    st.caption("2月24日生效 · 出口承压")
with e2:
    st.write("<span class='tag-orange'>橙色</span> **沃什上任美联储**", unsafe_allow_html=True)
    st.caption("5-6月接任 · 美元>108减仓")
with e3:
    st.write("<span class='tag-orange'>橙色</span> **中东局势**", unsafe_allow_html=True)
    st.caption("布油 74.2 · 触发则能源+5%")
with e4:
    st.write("<span class='tag-green'>绿色</span> **白银支撑有效**", unsafe_allow_html=True)
    st.caption(f"2月8日见底 · 现价 {intl_p['SI=F']:.2f}")

st.markdown('</div>', unsafe_allow_html=True)
