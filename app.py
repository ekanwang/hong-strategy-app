import streamlit as st
import pandas as pd
import yfinance as yf
import akshare as ak
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

# 1. 【极致保活】25秒心跳，兼顾保活与接口访问频率安全
st_autorefresh(interval=25000, key="honghao_final_shield")

st.set_page_config(layout="wide", page_title="Hao Hong Strategy Pro", page_icon="🛡️")

# --- 2. 深度黑金 UI 优化 (适配手机端高对比度) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .main-card {
        background: #1a1c24; padding: 18px; border-radius: 12px;
        border: 1px solid #2d2e3a; margin-bottom: 12px;
        border-top: 3px solid #f39c12;
    }
    .logic-card {
        background: #1e1e2e; padding: 15px; border-radius: 10px;
        border-left: 4px solid #10b981; margin-top: 10px;
    }
    .metric-label { font-size: 13px; color: #94a3b8; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: 800; font-family: 'Courier New', monospace; }
    /* 隐藏 Streamlit 默认页脚 */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 高可靠数据引擎 (伦敦现货 + 故障自动回滚) ---
@st.cache_data(ttl=15)
def get_verified_data():
    # 建立兜底数据（若接口全挂，显示洪灏提到的关键锚点）
    m = {"gold": 5136.35, "silver": 86.038, "oil": 71.05, "sh": 4082, "status": "Offline/Cached"}
    try:
        # 尝试获取伦敦现货数据
        # 使用 fast_info 提速，降低服务器不响应概率
        gold_tk = yf.Ticker("XAUUSD=X").fast_info
        silver_tk = yf.Ticker("XAGUSD=X").fast_info
        oil_tk = yf.Ticker("BZ=F").fast_info
        
        m["gold"] = gold_tk['last_price']
        m["silver"] = silver_tk['last_price']
        m["oil"] = oil_tk['last_price']
        
        # 尝试抓取上证指数 (akshare)
        try:
            sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
            m["sh"] = sh_df['latest'].values[0]
        except: pass
        
        m["status"] = "Live"
        return m
    except Exception:
        return m

data = get_verified_data()

# --- 4. 界面渲染 ---
st.markdown("### 🛡️ 洪灏策略交易终端")
st.caption(f"📡 {data['status']} | LONDON SPOT | {datetime.now().strftime('%H:%M:%S')}")

# 4.1 核心报价区
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'''<div class="main-card">
        <div class="metric-label">🌕 伦敦金现 (XAU)</div>
        <div class="metric-value" style="color:#f39c12">${data["gold"]:.2f}</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="main-card">
        <div class="metric-label">🛢️ 布伦特原油 (Brent)</div>
        <div class="metric-value">${data["oil"]:.2f}</div>
    </div>''', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="main-card">
        <div class="metric-label">⚪ 伦敦银现 (XAG)</div>
        <div class="metric-value">${data["silver"]:.3f}</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="main-card">
        <div class="metric-label">⚖️ 实时金银比 (G/S)</div>
        <div class="metric-value" style="color:#10b981">{(data["gold"]/data["silver"]):.1f}</div>
    </div>''', unsafe_allow_html=True)

# 4.2 洪灏：丙午之火·深度逻辑监控 (补齐最新更新)
st.markdown("---")
st.markdown("#### 📡 宏观逻辑监控 (基于 2.23 最新更新)")
with st.container():
    st.markdown(f"""
    <div class="logic-card">
        <b>🔥 丙午之火状态</b>: 周期顶峰 (75% 演进) <br>
        <b>🏛️ 关税逻辑更新</b>: 最高法院裁定裁决违宪 → 美元信用受损预期上升 → 避险脱钩<b>强度增加</b> <br>
        <b>💹 人民币逻辑</b>: 已触发升值重估 (目标 < 6.9)，带动上证指数 <b>{data['sh']}</b> 底部抬升 <br>
        <b>⚖️ 目标位</b>: 维持金银比回归 44-50 中线判断
    </div>
    """, unsafe_allow_html=True)

# 4.3 自选标的动态录入
st.markdown("---")
st.markdown("#### ⭐ 核心资产跟踪 (手机端可点 + 增加)")
if 'stock_table' not in st.session_state:
    st.session_state.stock_table = pd.DataFrame([
        {"标的": "江西铜业", "代码": "600362", "逻辑": "⚖️铜金双驱", "现价": 24.8},
        {"标的": "兴业矿业", "代码": "000426", "逻辑": "🥈白银Beta", "现价": 17.2},
        {"标的": "化工ETF", "代码": "516020", "逻辑": "🔥丙午之火对冲", "现价": 0.98}
    ])

# 动态编辑器：手机端点击表格底部的 (+) 按钮即可自由增加后续持仓标的
updated_df = st.data_editor(
    st.session_state.stock_table, 
    num_rows="dynamic", 
    use_container_width=True,
    key="stock_editor_final"
)
st.session_state.stock_table = updated_df

# 底部风险预警
st.error("⚠️ 风险监控：美国关税违宪退还 2000 亿债务风险，关注金价 5130 支撑。")
