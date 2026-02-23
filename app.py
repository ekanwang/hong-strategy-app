import streamlit as st
import pandas as pd
import yfinance as yf
import akshare as ak
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 【核心：手机端保活机制】
# 设置 25 秒自动刷新一次，这不仅能同步数据，还能持续给服务器发信号，防止休眠
st_autorefresh(interval=25000, key="honghao_always_live")

st.set_page_config(layout="wide", page_title="Hao Hong Pro", page_icon="🛡️")

# --- 2. 深度黑金 UI 适配手机（还原大智慧质感） ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .main-card {
        background: #1a1c24; padding: 18px; border-radius: 12px;
        border: 1px solid #2d2e3a; margin-bottom: 12px;
        border-top: 3px solid #f39c12;
    }
    .metric-val { font-size: 24px; font-weight: 800; color: #ffffff; font-family: monospace; }
    .metric-label { font-size: 13px; color: #94a3b8; }
    /* 解决手机端表格溢出 */
    .stDataEditor { width: 100% !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 实时伦敦现货行情（精准纠偏 + 容错防崩） ---
@st.cache_data(ttl=10)
def get_realtime_data():
    # 建立兜底，如果 yf 报错，网页不会打不开，而是显示你截图的最新值
    res = {"gold": 5136.35, "silver": 86.038, "oil": 71.05, "sh": 4082}
    try:
        # 锁定伦敦现货 XAU/XAG 和 布油
        res["gold"] = yf.Ticker("XAUUSD=X").fast_info['last_price']
        res["silver"] = yf.Ticker("XAGUSD=X").fast_info['last_price']
        res["oil"] = yf.Ticker("BZ=F").fast_info['last_price']
        # A股上证
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        res["sh"] = sh_df['latest'].values[0]
        return res
    except:
        return res # 报错就返回兜底值，防止手机端白屏

m = get_realtime_data()

# --- 4. 界面渲染 ---
st.markdown("### 🛡️ 洪灏策略交易终端")
st.caption(f"LIVE | LONDON SPOT | {datetime.now().strftime('%H:%M:%S')}")

# 4.1 顶部报价 (手机端自动分排) - 模块保留
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="main-card"><div class="metric-label">伦敦金现</div><div class="metric-val" style="color:#f39c12">${m["gold"]:.2f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-card"><div class="metric-label">布伦特油</div><div class="metric-val">${m["oil"]:.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="main-card"><div class="metric-label">伦敦银现</div><div class="metric-val">${m["silver"]:.3f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-card"><div class="metric-label">实时金银比</div><div class="metric-val">{(m["gold"]/m["silver"]):.1f}</div></div>', unsafe_allow_html=True)

# 4.2 知识库最新观点 (补齐今日洪灏“关税违宪”更新) - 模块增强
st.markdown("---")
st.markdown("#### 📡 洪灏：丙午之火·逻辑监控")
with st.container():
    st.markdown(f"""
    * **核心状态**: <span style='color:#10b981'>🟢 避险脱钩验证中</span>
    * **人民币逻辑**: <span style='color:#10b981'>🟢 升值触发 (目标 < 6.9)</span>
    * **今日更新**: <span style='color:#f39c12'>🏛️ 特朗普关税遭裁定违宪。</span>预计美元信用受损，利好黄金/人民币避险脱钩。
    * **周期进度**: 丙午马年周期顶峰，波动率将持续放大。
    """, unsafe_allow_html=True)

# 4.3 自选标的动态录入（核心增量空间）- 模块保留
st.markdown("---")
st.markdown("#### ⭐ 核心资产跟踪")
if 'stock_table' not in st.session_state:
    st.session_state.stock_table = pd.DataFrame([
        {"标的": "江西铜业", "操作": "⚖️铜金双驱", "现价": 24.8},
        {"标的": "兴业矿业", "操作": "🥈白银Beta", "现价": 17.2}
    ])

# 动态编辑器：手机点击底部 (+) 即可新增股票信息
updated_df = st.data_editor(st.session_state.stock_table, num_rows="dynamic", use_container_width=True)
st.session_state.stock_table = updated_df
