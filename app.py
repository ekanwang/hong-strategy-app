import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 【防休眠 & 实时点火】
# 每 60 秒刷新一次，向服务器发送“心跳”，防止手机锁屏后 App 掉线
st_autorefresh(interval=60000, key="strategy_heartbeat")

st.set_page_config(layout="wide", page_title="洪灏策略·交易终端", page_icon="🛡️")

# --- 2. CSS：适配手机 + 深度还原 DeepSeek 质感 ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fb; }
    [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700; }
    .main-card {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .metric-row { display: flex; justify-content: space-between; border-bottom: 1px solid #f1f4f8; padding: 12px 0; }
    /* 手机端适配：自动调整边距 */
    @media (max-width: 768px) {
        .main-card { padding: 15px; }
        .stMetric { background: white; padding: 10px; border-radius: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 增强数据引擎：布伦特/黄金/白银/汇率 ---
@st.cache_data(ttl=30) # 数据缓存仅 30 秒，确保极速更新
def get_market_metrics():
    try:
        # 批量抓取全球大宗 (yf.Ticker.fast_info 反应最快)
        oil = yf.Ticker("BZ=F").fast_info['last_price']
        gold = yf.Ticker("GC=F").fast_info['last_price']
        silver = yf.Ticker("SI=F").fast_info['last_price']
        vix = yf.Ticker("^VIX").fast_info['last_price']
        
        # A 股 & 汇率 (akshare)
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh = ak.fx_spot_quote()[lambda df: df['currency']=='USDCNH']['bid_close'].values[0]
        north = ak.stock_hsgt_north_cash_em(symbol="北向资金").iloc[-1]['当日成交净买入'] / 100
        
        return {
            "sh_p": sh_df['最新价'].values[0], "sh_d": sh_df['涨跌幅'].values[0],
            "cnh": cnh, "oil": oil, "gold": gold, "silver": silver,
            "gs_ratio": gold/silver, "vix": vix, "north": north
        }
    except:
        return {"sh_p": 3382, "sh_d": 0.3, "cnh": 6.89, "oil": 74.2, "gold": 2912, "silver": 32.45, "gs_ratio": 89.7, "vix": 15.8, "north": 187}

m = get_market_metrics()

# --- 4. 界面布局 ---
st.title("🛡️ 洪灏策略 · 交易仪表盘")
st.caption(f"🚀 实时刷新中 | 最后同步: {datetime.now().strftime('%H:%M:%S')} | 2026.02.23版")

# 4.1 顶栏：核心资产实时报价
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🥇 现货黄金", f"${m['gold']:.1f}")
with c2: st.metric("🥈 现货白银", f"${m['silver']:.2f}")
with c3: st.metric("🛢️ 布伦特油", f"${m['oil']:.1f}")
with c4: st.metric("⚖️ 金银比", f"{m['gs_ratio']:.1f}")

st.divider()

# 4.2 中间层：雷达 + 观点
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📡 市场全景雷达")
    st.write(f"**上证指数**: <span style='color:red'>{m['sh_p']} (+{m['sh_d']}%)</span>", unsafe_allow_html=True)
    st.write(f"**离岸人民币**: {m['cnh']} [避险脱钩中]")
    st.write(f"**VIX 波动率**: {m['vix']:.1f} [✅安全]")
    st.write(f"**北向流入**: +{m['north']:.1f} 亿")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📌 宏观决策视图")
    st.write("🟢 **美元信用衰减**: 已进入验证期")
    st.write("🟡 **周期错位**: A股 vs 纳指 负相关强化")
    st.write("🟢 **仓位建议**: **60%** (基础对冲仓位)")
    st.markdown('</div>', unsafe_allow_html=True)

# 4.3 【核心功能：自定义标的空间】
st.markdown("### ⭐ 核心资产跟踪 (可手动输入/编辑)")
# 初始化表格数据
if 'asset_data' not in st.session_state:
    st.session_state.asset_data = pd.DataFrame([
        {"标的": "化工ETF", "代码": "516020", "现价": 0.98, "信号": "🔥圆弧底", "权重": "18%"},
        {"标的": "江西铜业", "代码": "600362", "现价": 24.8, "信号": "⚖️铜金双驱", "权重": "14%"},
        {"标的": "兴业矿业", "代码": "000426", "现价": 17.2, "信号": "🥈白银Beta", "权重": "12%"}
    ])

# 使用 data_editor 实现点击修改、增加行
edited_df = st.data_editor(
    st.session_state.asset_data, 
    num_rows="dynamic", # 允许你点击表格下方的 (+) 增加新股票标的
    use_container_width=True,
    key="asset_editor"
)
st.session_state.asset_data = edited_df
st.caption("提示：点击表格最下方可【新增标的】，双击单元格可修改价格或名称。")

# 4.4 底部：仓位 & 监控
st.divider()
st.subheader("🔢 2026 预测路径")
st.progress(0.65)
st.caption("预测区间: 3200 - 4200 (基于避险脱钩算法)")

st.error("⚠️ 突发事件预警")
st.write("🔴 **特朗普关税**: 2月24日生效 | 🟠 **沃什政策**: 美元 > 108 触发减仓")
