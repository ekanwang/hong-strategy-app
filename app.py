import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 每60秒自动刷新，保持实时更新
st_autorefresh(interval=60000, key="global_refresh")

st.set_page_config(layout="wide", page_title="洪灏策略交易仪表盘")

# --- 数据抓取引擎 (含周末兼容) ---
@st.cache_data(ttl=50)
def get_data():
    # 国际行情
    intl = yf.download(["GC=F", "SI=F", "^VIX", "CL=F"], period="2d", interval="1d")['Close'].iloc[-1]
    # 国内行情
    try:
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_data = ak.fx_spot_quote()
        cnh_val = cnh_data[cnh_data['currency'] == 'USDCNH']['bid_close'].values[0]
        sh_val = sh_df['最新价'].values[0]
    except:
        sh_val, cnh_val = "休市中", "7.1x"
    return intl, sh_val, cnh_val

# --- UI 布局复刻 ---
st.title("📊 洪灏策略 · 交易仪表盘 (实时版)")
intl_prices, sh_idx, cnh_price = get_data()

# 1. 顶部宏观指标 [对应图片左侧雷达]
c1, c2, c3, c4 = st.columns(4)
c1.metric("上证指数", f"{sh_idx}")
c2.metric("离岸人民币 (CNH)", f"{cnh_price}")
gs_ratio = intl_prices['GC=F'] / intl_prices['SI=F']
c3.metric("实时金银比", f"{gs_ratio:.2f}", "目标: 44", delta_color="inverse")
c4.metric("VIX 波动率", f"{intl_prices['^VIX']:.2f}", "安全" if intl_prices['^VIX'] < 20 else "高风险")

# 2. 核心资产追踪 [满足随时调整持仓的需求]
st.divider()
st.subheader("⭐ 核心资产动态追踪")
st.info("💡 提示：你可以直接在下表中修改股票代码或止损价，行情将实时重算。")

# 初始化默认持仓 [对应图片自选池]
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "目标": 1.20, "止损": 0.90},
        {"标的": "江西铜业", "代码": "600362", "目标": 32.0, "止损": 22.0},
        {"标的": "工商银行", "代码": "601398", "目标": 7.00, "止损": 5.70},
        {"标的": "科大讯飞", "代码": "002230", "目标": 65.0, "止损": 45.0}
    ])

# 动态编辑表格
edited_df = st.data_editor(st.session_state.portfolio, num_rows="dynamic")

# 实时计算逻辑
stocks_all = ak.stock_zh_a_spot_em()
results = []
for _, row in edited_df.iterrows():
    match = stocks_all[stocks_all['代码'] == str(row['代码']).zfill(6)]
    if not match.empty:
        curr = match['最新价'].values[0]
        status = "✅ 持有" if curr > row['止损'] else "🚨 触发止损"
        results.append({
            "名称": row['标的'], "现价": curr, 
            "涨跌": f"{match['涨跌幅'].values[0]}%", 
            "止损线": row['止损'], "状态": status
        })

if results:
    st.table(pd.DataFrame(results))

# 3. 2026 预测区间 [对应图片中部进度条]
st.divider()
st.subheader("📅 2026 预测点位监控")
p_col = st.columns(1)[0]
if isinstance(sh_idx, (int, float)):
    progress = min(max((sh_idx - 3200) / 400, 0.0), 1.0) # 以 Q1 区间 3200-3600 为例
    p_col.write(f"当前点位在 Q1 区间 (3200-3600) 的位置：")
    p_col.progress(progress)

st.caption(f"最后同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 策略逻辑由洪灏宏观框架驱动")
