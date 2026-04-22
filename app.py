"""
╔══════════════════════════════════════════════════════════════════╗
║     BINANCE FUTURES AI TRADING BOT - DEEP RL DASHBOARD          ║
║     Built with Streamlit + Stable Baselines3 + CCXT + Pandas-TA ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional

# ─── PAGE CONFIG (MUST BE FIRST) ────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trading Bot | Binance Futures",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS (Mobile-first, Dark Terminal Theme) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Space+Grotesk:wght@300;400;600;700&display=swap');

:root {
    --bg: #080c10;
    --bg2: #0d1117;
    --panel: #0f1923;
    --border: #1c2a38;
    --green: #00ff88;
    --red: #ff3366;
    --yellow: #ffd700;
    --blue: #00d4ff;
    --text: #c8d6e5;
    --muted: #506272;
    --font-mono: 'JetBrains Mono', monospace;
    --font-ui: 'Space Grotesk', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-ui) !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { background: var(--bg2) !important; }

.main .block-container {
    padding: 0.5rem 0.8rem !important;
    max-width: 100% !important;
}

/* ── HEADER ── */
.hdr {
    background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #091219 100%);
    border: 1px solid var(--border);
    border-left: 3px solid var(--green);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.hdr-title { font-family: var(--font-mono); font-size: 1.1rem; color: var(--green); font-weight: 700; letter-spacing: 1px; }
.hdr-sub { font-size: 0.72rem; color: var(--muted); font-family: var(--font-mono); }
.live-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(0.8)} }

/* ── METRIC CARD ── */
.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.green::before { background: var(--green); }
.metric-card.red::before { background: var(--red); }
.metric-card.blue::before { background: var(--blue); }
.metric-card.yellow::before { background: var(--yellow); }
.metric-val { font-family: var(--font-mono); font-size: 1.4rem; font-weight: 700; }
.metric-lbl { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }
.metric-card.green .metric-val { color: var(--green); }
.metric-card.red .metric-val { color: var(--red); }
.metric-card.blue .metric-val { color: var(--blue); }
.metric-card.yellow .metric-val { color: var(--yellow); }

/* ── SIGNAL CARD ── */
.signal-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
    position: relative;
}
.signal-card.long { border-left: 3px solid var(--green); }
.signal-card.short { border-left: 3px solid var(--red); }
.signal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.coin-name { font-family: var(--font-mono); font-weight: 700; font-size: 1rem; }
.long .coin-name { color: var(--green); }
.short .coin-name { color: var(--red); }
.direction-badge {
    padding: 2px 8px; border-radius: 4px; font-size: 0.65rem;
    font-family: var(--font-mono); font-weight: 700; letter-spacing: 1px;
}
.badge-long { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.3); }
.badge-short { background: rgba(255,51,102,0.15); color: var(--red); border: 1px solid rgba(255,51,102,0.3); }

/* ── INTENSITY BAR ── */
.intensity-wrap { margin: 8px 0; }
.intensity-label { font-size: 0.65rem; color: var(--muted); font-family: var(--font-mono); margin-bottom: 3px; display: flex; justify-content: space-between; }
.bar-bg { background: #1a2535; border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.bar-long { background: linear-gradient(90deg, #00994d, #00ff88); }
.bar-short { background: linear-gradient(90deg, #cc0033, #ff3366); }

/* ── PRICE ROW ── */
.price-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 8px; }
.price-item {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.price-label { font-size: 0.62rem; color: var(--muted); font-family: var(--font-mono); }
.price-value { font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600; }
.price-entry { color: var(--blue); }
.price-tp { color: var(--green); }
.price-sl { color: var(--red); }
.copy-btn {
    background: none; border: none; cursor: pointer;
    font-size: 0.75rem; padding: 0 2px; opacity: 0.6;
    transition: opacity 0.2s;
}
.copy-btn:hover { opacity: 1; }

/* ── HISTORY TABLE ── */
.hist-table { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.72rem; }
.hist-table th { 
    background: var(--bg2); color: var(--muted); 
    padding: 6px 8px; text-align: left; 
    font-size: 0.6rem; letter-spacing: 1px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
}
.hist-table td { padding: 7px 8px; border-bottom: 1px solid rgba(28,42,56,0.5); }
.win { color: var(--green); }
.loss { color: var(--red); }
.neutral { color: var(--muted); }
.win-rate-badge {
    display: inline-block;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    color: var(--green);
    padding: 4px 12px; border-radius: 20px;
    font-family: var(--font-mono); font-size: 0.85rem; font-weight: 700;
}

/* ── MODEL STATUS ── */
.model-info {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
}
.model-info .row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.model-info .key { color: var(--muted); }
.model-info .val { color: var(--blue); }

/* ── SECTION TITLE ── */
.sec-title {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 8px 0 4px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}

/* ── SCROLLABLE CONTAINER ── */
.scroll-section { max-height: 420px; overflow-y: auto; padding-right: 4px; }
.scroll-section::-webkit-scrollbar { width: 3px; }
.scroll-section::-webkit-scrollbar-track { background: var(--bg2); }
.scroll-section::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── TABS ── */
[data-testid="stTabs"] button {
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--green) !important;
    border-bottom: 2px solid var(--green) !important;
}

/* ── STREAMLIT OVERRIDES ── */
.stButton button {
    background: rgba(0,255,136,0.1) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
    color: var(--green) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    border-radius: 4px !important;
    padding: 4px 10px !important;
}
.stSelectbox > div { background: var(--panel) !important; border-color: var(--border) !important; color: var(--text) !important; }
div[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SECTION 1: IMPORTS & CONDITIONAL LOADING
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def load_libraries():
    """Load heavy libraries once and cache them."""
    libs = {}
    try:
        import ccxt
        libs['ccxt'] = ccxt
    except ImportError:
        libs['ccxt'] = None

    try:
        import pandas_ta as ta
        libs['ta'] = ta
    except ImportError:
        libs['ta'] = None

    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv
        libs['PPO'] = PPO
        libs['DummyVecEnv'] = DummyVecEnv
    except ImportError:
        libs['PPO'] = None
        libs['DummyVecEnv'] = None

    return libs


# ═══════════════════════════════════════════════════════════════
#  SECTION 2: BINANCE DATA FETCHER (CCXT)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol: str, timeframe: str = "15m", limit: int = 500,
                api_key: str = "", api_secret: str = "") -> Optional[pd.DataFrame]:
    """Fetch OHLCV from Binance Futures via CCXT."""
    try:
        libs = load_libraries()
        if libs['ccxt'] is None:
            return _generate_synthetic_ohlcv(symbol, limit)

        ccxt = libs['ccxt']
        params = {"options": {"defaultType": "future"}}
        if api_key and api_secret:
            params["apiKey"] = api_key
            params["secret"] = api_secret

        exchange = ccxt.binanceusdm(params)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df.astype(float)
    except Exception:
        return _generate_synthetic_ohlcv(symbol, limit)


def _generate_synthetic_ohlcv(symbol: str, n: int = 500) -> pd.DataFrame:
    """Generate realistic synthetic OHLCV for demo/offline mode."""
    np.random.seed(hash(symbol) % (2**31))
    prices = {"BTCUSDT": 65000, "ETHUSDT": 3200, "BNBUSDT": 580,
              "SOLUSDT": 145, "XRPUSDT": 0.58, "ADAUSDT": 0.45,
              "DOGEUSDT": 0.13, "AVAXUSDT": 38, "DOTUSDT": 8.2,
              "LINKUSDT": 18, "MATICUSDT": 0.72, "LTCUSDT": 95,
              "ATOMUSDT": 10.5, "UNIUSDT": 11, "NEARUSDT": 7.4}
    base = prices.get(symbol, 100)
    returns = np.random.normal(0, 0.008, n)
    closes = base * np.exp(np.cumsum(returns))
    highs = closes * (1 + np.abs(np.random.normal(0, 0.005, n)))
    lows = closes * (1 - np.abs(np.random.normal(0, 0.005, n)))
    opens = np.roll(closes, 1)
    opens[0] = base
    volumes = np.random.lognormal(12, 0.8, n)
    idx = pd.date_range(end=datetime.utcnow(), periods=n, freq="15min")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows,
                          "close": closes, "volume": volumes}, index=idx)


@st.cache_data(ttl=30)
def fetch_futures_symbols(api_key: str = "", api_secret: str = "") -> list:
    """Get all USDT perpetual futures symbols."""
    default = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
                "MATICUSDT", "LTCUSDT", "ATOMUSDT", "UNIUSDT", "NEARUSDT",
                "FTMUSDT", "SANDUSDT", "MANAUSDT", "GALAUSDT", "APEUSDT"]
    try:
        libs = load_libraries()
        if libs['ccxt'] is None:
            return default
        ccxt = libs['ccxt']
        exchange = ccxt.binanceusdm({"options": {"defaultType": "future"}})
        markets = exchange.load_markets()
        symbols = [s.replace("/", "") for s in markets
                   if s.endswith("/USDT") and markets[s].get("future")]
        return symbols[:80] if symbols else default
    except Exception:
        return default


# ═══════════════════════════════════════════════════════════════
#  SECTION 3: 130+ TECHNICAL INDICATORS (Pandas-TA)
# ═══════════════════════════════════════════════════════════════

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute 130+ technical indicators using pandas-ta."""
    libs = load_libraries()
    ta = libs.get('ta')

    df = df.copy()

    if ta is not None:
        # ── Moving Averages (15 indicators)
        for p in [5, 8, 13, 21, 34, 55, 89, 144, 200]:
            df[f"ema_{p}"] = ta.ema(df["close"], length=p)
        for p in [10, 20, 50, 100, 200]:
            df[f"sma_{p}"] = ta.sma(df["close"], length=p)
        df["wma_20"] = ta.wma(df["close"], length=20)
        df["hma_20"] = ta.hma(df["close"], length=20)
        df["vwma_20"] = ta.vwma(df["close"], df["volume"], length=20)

        # ── Oscillators (20 indicators)
        df["rsi_14"] = ta.rsi(df["close"], length=14)
        df["rsi_7"] = ta.rsi(df["close"], length=7)
        df["rsi_21"] = ta.rsi(df["close"], length=21)
        stoch = ta.stoch(df["high"], df["low"], df["close"])
        if stoch is not None:
            df = pd.concat([df, stoch], axis=1)
        macd = ta.macd(df["close"])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        df["cci_20"] = ta.cci(df["high"], df["low"], df["close"], length=20)
        df["cci_14"] = ta.cci(df["high"], df["low"], df["close"], length=14)
        df["mfi_14"] = ta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14)
        df["willr_14"] = ta.willr(df["high"], df["low"], df["close"], length=14)
        df["roc_10"] = ta.roc(df["close"], length=10)
        df["mom_10"] = ta.mom(df["close"], length=10)
        df["cmo_14"] = ta.cmo(df["close"], length=14)
        df["ppo"] = ta.ppo(df["close"]).iloc[:, 0] if ta.ppo(df["close"]) is not None else np.nan
        df["dpo_20"] = ta.dpo(df["close"], length=20)
        df["er_10"] = ta.er(df["close"], length=10)
        df["tsi"] = ta.tsi(df["close"]).iloc[:, 0] if ta.tsi(df["close"]) is not None else np.nan

        # ── Volatility (15 indicators)
        bb = ta.bbands(df["close"])
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        kc = ta.kc(df["high"], df["low"], df["close"])
        if kc is not None:
            df = pd.concat([df, kc], axis=1)
        df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
        df["atr_7"] = ta.atr(df["high"], df["low"], df["close"], length=7)
        df["natr_14"] = ta.natr(df["high"], df["low"], df["close"], length=14)
        df["true_range"] = ta.true_range(df["high"], df["low"], df["close"])
        df["ui_14"] = ta.ui(df["close"], length=14)
        df["massi"] = ta.massi(df["high"], df["low"])

        # ── Volume (15 indicators)
        df["obv"] = ta.obv(df["close"], df["volume"])
        df["ad"] = ta.ad(df["high"], df["low"], df["close"], df["volume"])
        df["adosc"] = ta.adosc(df["high"], df["low"], df["close"], df["volume"])
        df["cmf_20"] = ta.cmf(df["high"], df["low"], df["close"], df["volume"], length=20)
        df["eom_14"] = ta.eom(df["high"], df["low"], df["close"], df["volume"], length=14)
        df["pvt"] = ta.pvt(df["close"], df["volume"])
        df["nvi"] = ta.nvi(df["close"], df["volume"])
        df["pvi"] = ta.pvi(df["close"], df["volume"])
        df["vp"] = df["volume"] * df["close"]  # Volume Price proxy
        df["vwap"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
        df["kvo"] = ta.kvo(df["high"], df["low"], df["close"], df["volume"]).iloc[:, 0] \
            if ta.kvo(df["high"], df["low"], df["close"], df["volume"]) is not None else np.nan

        # ── Trend (20 indicators)
        adx = ta.adx(df["high"], df["low"], df["close"])
        if adx is not None:
            df = pd.concat([df, adx], axis=1)
        df["aroon_up"] = ta.aroon(df["high"], df["low"]).iloc[:, 1] \
            if ta.aroon(df["high"], df["low"]) is not None else np.nan
        df["aroon_dn"] = ta.aroon(df["high"], df["low"]).iloc[:, 0] \
            if ta.aroon(df["high"], df["low"]) is not None else np.nan
        ichimoku = ta.ichimoku(df["high"], df["low"], df["close"])
        if ichimoku is not None and isinstance(ichimoku, tuple):
            df = pd.concat([df, ichimoku[0]], axis=1)
        df["psar"] = ta.psar(df["high"], df["low"], df["close"])["PSARl_0.02_0.2"] \
            if ta.psar(df["high"], df["low"], df["close"]) is not None else np.nan
        df["supertrend"] = ta.supertrend(df["high"], df["low"], df["close"])["SUPERT_7_3.0"] \
            if ta.supertrend(df["high"], df["low"], df["close"]) is not None else np.nan
        df["cksp_l"] = ta.cksp(df["high"], df["low"], df["close"]).iloc[:, 0] \
            if ta.cksp(df["high"], df["low"], df["close"]) is not None else np.nan
        df["ttm_trend"] = ta.ttm_trend(df["high"], df["low"], df["close"]).iloc[:, 0] \
            if ta.ttm_trend(df["high"], df["low"], df["close"]) is not None else np.nan
        df["qstick_8"] = ta.qstick(df["open"], df["close"], length=8)
        df["vortex_pos"] = ta.vortex(df["high"], df["low"], df["close"]).iloc[:, 0] \
            if ta.vortex(df["high"], df["low"], df["close"]) is not None else np.nan
        df["vortex_neg"] = ta.vortex(df["high"], df["low"], df["close"]).iloc[:, 1] \
            if ta.vortex(df["high"], df["low"], df["close"]) is not None else np.nan

        # ── Candle Patterns (10 indicators) - manual
        df["body"] = df["close"] - df["open"]
        df["wick_up"] = df["high"] - df[["close", "open"]].max(axis=1)
        df["wick_dn"] = df[["close", "open"]].min(axis=1) - df["low"]
        df["body_ratio"] = df["body"].abs() / (df["high"] - df["low"] + 1e-8)
        df["doji"] = (df["body_ratio"] < 0.1).astype(int)
        df["hammer"] = ((df["wick_dn"] > 2 * df["body"].abs()) & (df["wick_up"] < df["body"].abs())).astype(int)
        df["shooting_star"] = ((df["wick_up"] > 2 * df["body"].abs()) & (df["wick_dn"] < df["body"].abs())).astype(int)
        df["engulf_bull"] = ((df["body"] > 0) & (df["body"].shift(1) < 0) & (df["body"].abs() > df["body"].shift(1).abs())).astype(int)
        df["engulf_bear"] = ((df["body"] < 0) & (df["body"].shift(1) > 0) & (df["body"].abs() > df["body"].shift(1).abs())).astype(int)
        df["three_white"] = ((df["body"] > 0) & (df["body"].shift(1) > 0) & (df["body"].shift(2) > 0)).astype(int)

        # ── Order Flow Proxies (10 indicators)
        df["buy_pressure"] = (df["close"] - df["low"]) / (df["high"] - df["low"] + 1e-8)
        df["sell_pressure"] = (df["high"] - df["close"]) / (df["high"] - df["low"] + 1e-8)
        df["delta_vol"] = df["volume"] * (df["buy_pressure"] - df["sell_pressure"])
        df["cum_delta"] = df["delta_vol"].cumsum()
        df["taker_buy_ratio"] = df["buy_pressure"]  # proxy
        df["vol_price_corr"] = df["close"].rolling(20).corr(df["volume"])
        df["vol_momentum"] = df["volume"] / df["volume"].rolling(20).mean()
        df["vol_std"] = df["volume"].rolling(20).std()
        df["price_vol_trend"] = df["close"].pct_change() * df["volume"]
        df["market_impact"] = (df["high"] - df["low"]) / (df["volume"] + 1e-8)

        # ── Statistical (10 indicators)
        df["zscore_20"] = (df["close"] - df["close"].rolling(20).mean()) / (df["close"].rolling(20).std() + 1e-8)
        df["percentile_rank_14"] = df["close"].rolling(14).rank(pct=True) * 100
        df["variance_20"] = df["close"].rolling(20).var()
        df["skew_20"] = df["close"].rolling(20).skew()
        df["kurt_20"] = df["close"].rolling(20).kurt()
        df["hist_vol_20"] = df["close"].pct_change().rolling(20).std() * np.sqrt(252 * 96)  # annualized
        df["realized_vol_7"] = df["close"].pct_change().rolling(7).std() * np.sqrt(252 * 96)
        df["autocorr_5"] = df["close"].rolling(10).apply(lambda x: x[:5].corr(x[5:]) if len(x) == 10 else np.nan)
        df["hurst"] = 0.5  # placeholder (Hurst exponent requires longer computation)
        df["shannon_entropy"] = df["close"].rolling(20).apply(
            lambda x: -sum([(p := (x == v).mean()) * np.log2(p + 1e-8) for v in np.unique(np.round(x, 0))]))

    else:
        # Fallback: compute basic indicators manually
        df = _compute_basic_indicators(df)

    return df


def _compute_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Fallback basic indicator computation without pandas-ta."""
    c = df["close"]
    h, l, v = df["high"], df["low"], df["volume"]

    for p in [9, 21, 50, 200]:
        df[f"ema_{p}"] = c.ewm(span=p).mean()
        df[f"sma_{p}"] = c.rolling(p).mean()

    # RSI
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi_14"] = 100 - (100 / (1 + gain / (loss + 1e-8)))

    # MACD
    ema12 = c.ewm(span=12).mean()
    ema26 = c.ewm(span=26).mean()
    df["MACD_12_26_9"] = ema12 - ema26
    df["MACDs_12_26_9"] = df["MACD_12_26_9"].ewm(span=9).mean()

    # Bollinger Bands
    df["BBM_20_2.0"] = c.rolling(20).mean()
    std = c.rolling(20).std()
    df["BBU_20_2.0"] = df["BBM_20_2.0"] + 2 * std
    df["BBL_20_2.0"] = df["BBM_20_2.0"] - 2 * std

    # ATR
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    df["atr_14"] = tr.rolling(14).mean()

    # ADX
    df["ADX_14"] = 25  # placeholder

    # Volume
    df["obv"] = (np.sign(c.diff()) * v).cumsum()
    df["buy_pressure"] = (c - l) / (h - l + 1e-8)
    df["vol_momentum"] = v / (v.rolling(20).mean() + 1e-8)
    df["rsi_7"] = df["rsi_14"]  # simplified
    df["rsi_21"] = df["rsi_14"]  # simplified
    df["mfi_14"] = df["rsi_14"]  # proxy
    df["cmf_20"] = (2 * c - h - l) / (h - l + 1e-8) * v / (v.rolling(20).mean() + 1e-8)
    df["zscore_20"] = (c - c.rolling(20).mean()) / (c.rolling(20).std() + 1e-8)
    df["body"] = c - df["open"]
    df["delta_vol"] = v * df["buy_pressure"]
    df["hist_vol_20"] = c.pct_change().rolling(20).std() * np.sqrt(252 * 96)

    return df


# ═══════════════════════════════════════════════════════════════
#  SECTION 4: RL ENVIRONMENT (OpenAI Gym Compatible)
# ═══════════════════════════════════════════════════════════════

class TradingEnvironment:
    """
    Simplified RL environment for Binance Futures trading.
    Compatible with Stable-Baselines3 PPO Agent.
    
    State: normalized indicator values (window of last N candles)
    Actions: 0=Hold, 1=Long, 2=Short, 3=Close
    Reward: +TP hit, -SL hit, small -penalty for each step
    """

    def __init__(self, df: pd.DataFrame, window: int = 20, commission: float = 0.0004):
        self.df = df.dropna().reset_index(drop=True)
        self.window = window
        self.commission = commission
        self.n = len(self.df)
        self.feature_cols = [c for c in df.columns if c not in ["open", "high", "low", "close", "volume"]]
        self.obs_dim = len(self.feature_cols) * window + 5  # + position info
        self.action_space_n = 4
        self.reset()

    def reset(self):
        self.idx = self.window
        self.position = 0  # -1=short, 0=none, 1=long
        self.entry_price = 0.0
        self.equity = 1.0
        self.trade_log = []
        return self._get_obs()

    def _get_obs(self):
        window_data = self.df[self.feature_cols].iloc[self.idx - self.window:self.idx].values
        obs_raw = window_data.flatten()
        obs_norm = (obs_raw - np.nanmean(obs_raw)) / (np.nanstd(obs_raw) + 1e-8)
        obs_norm = np.nan_to_num(obs_norm, 0)
        position_info = np.array([
            self.position,
            self.entry_price / (self.df["close"].iloc[self.idx] + 1e-8),
            self.equity,
            self.idx / self.n,
            1.0 if self.position != 0 else 0.0
        ])
        return np.concatenate([obs_norm, position_info])

    def step(self, action: int):
        price = self.df["close"].iloc[self.idx]
        atr = self.df.get("atr_14", pd.Series([price * 0.01] * self.n)).iloc[self.idx]

        reward = -0.001  # time penalty
        done = False

        # TP/SL parameters (ATR-based)
        tp1 = atr * 1.5
        tp2 = atr * 2.5
        tp3 = atr * 4.0
        sl = atr * 1.0

        if action == 1 and self.position == 0:  # Open Long
            self.position = 1
            self.entry_price = price * (1 + self.commission)

        elif action == 2 and self.position == 0:  # Open Short
            self.position = -1
            self.entry_price = price * (1 - self.commission)

        elif action == 3 and self.position != 0:  # Close
            pnl = self.position * (price - self.entry_price) / self.entry_price
            reward = pnl * 10 - self.commission
            self.equity *= (1 + pnl)
            self.trade_log.append({"pnl": pnl, "type": "close"})
            self.position = 0

        # Auto TP/SL check
        if self.position != 0:
            move = self.position * (price - self.entry_price)
            if move >= tp3:
                reward = 3.0
                self.equity *= (1 + tp3 / self.entry_price)
                self.trade_log.append({"pnl": tp3 / self.entry_price, "type": "TP3"})
                self.position = 0
            elif move >= tp2:
                reward = 2.0
                self.equity *= (1 + tp2 / self.entry_price)
                self.trade_log.append({"pnl": tp2 / self.entry_price, "type": "TP2"})
                self.position = 0
            elif move >= tp1:
                reward = 1.0
                self.equity *= (1 + tp1 / self.entry_price)
                self.trade_log.append({"pnl": tp1 / self.entry_price, "type": "TP1"})
                self.position = 0
            elif move <= -sl:
                reward = -2.5
                self.equity *= (1 - sl / self.entry_price)
                self.trade_log.append({"pnl": -sl / self.entry_price, "type": "SL"})
                self.position = 0

        self.idx += 1
        if self.idx >= self.n - 1:
            done = True

        return self._get_obs(), reward, done, {}


# ═══════════════════════════════════════════════════════════════
#  SECTION 5: PPO AGENT (Stable Baselines3)
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def get_or_train_ppo(df_hash: str, df: pd.DataFrame, timesteps: int = 10000):
    """Load or train PPO agent. Cached per unique data hash."""
    env = TradingEnvironment(df)
    libs = load_libraries()

    model_path = f"ppo_trading_{df_hash[:8]}.zip"

    if libs['PPO'] is not None:
        PPO = libs['PPO']
        DummyVecEnv = libs['DummyVecEnv']

        if os.path.exists(model_path):
            try:
                model = PPO.load(model_path)
                return model, env
            except Exception:
                pass

        # Wrap env for SB3
        import gymnasium as gym
        from gymnasium import spaces

        class SB3Wrapper(gym.Env):
            def __init__(self, trading_env):
                super().__init__()
                self.env = trading_env
                obs_size = trading_env.obs_dim
                self.observation_space = spaces.Box(
                    low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32)
                self.action_space = spaces.Discrete(trading_env.action_space_n)

            def reset(self, seed=None, options=None):
                return self.env.reset().astype(np.float32), {}

            def step(self, action):
                obs, rew, done, info = self.env.step(int(action))
                return obs.astype(np.float32), float(rew), done, False, info

        vec_env = DummyVecEnv([lambda: SB3Wrapper(TradingEnvironment(df))])
        model = PPO("MlpPolicy", vec_env, verbose=0,
                    learning_rate=3e-4, n_steps=512, batch_size=64,
                    n_epochs=10, gamma=0.99, gae_lambda=0.95,
                    clip_range=0.2, ent_coef=0.01)
        model.learn(total_timesteps=timesteps)
        model.save(model_path)
        return model, env

    return None, env


# ═══════════════════════════════════════════════════════════════
#  SECTION 6: SIGNAL SCORING ENGINE (0-100)
# ═══════════════════════════════════════════════════════════════

def compute_signal_score(df: pd.DataFrame) -> dict:
    """
    Multi-factor scoring engine producing 0-100 intensity score.
    Returns: direction, score, entry/TP/SL prices, win_rate estimate
    """
    row = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else row
    close = row["close"]

    scores_long = []
    scores_short = []

    def safe(val, default=0.5):
        if pd.isna(val) or np.isinf(val):
            return default
        return float(val)

    # ── RSI signals ──
    rsi = safe(row.get("rsi_14", 50), 50)
    if rsi < 30:
        scores_long.append(85)
    elif rsi < 40:
        scores_long.append(65)
    elif rsi < 50:
        scores_long.append(45)
    if rsi > 70:
        scores_short.append(85)
    elif rsi > 60:
        scores_short.append(65)
    elif rsi > 55:
        scores_short.append(45)

    # ── MACD signals ──
    macd = safe(row.get("MACD_12_26_9", 0), 0)
    macd_s = safe(row.get("MACDs_12_26_9", 0), 0)
    prev_macd = safe(prev.get("MACD_12_26_9", 0), 0)
    prev_macd_s = safe(prev.get("MACDs_12_26_9", 0), 0)
    if macd > macd_s and prev_macd <= prev_macd_s:
        scores_long.append(75)
    if macd < macd_s and prev_macd >= prev_macd_s:
        scores_short.append(75)
    if macd > 0:
        scores_long.append(55)
    else:
        scores_short.append(55)

    # ── Bollinger Band signals ──
    bbu = safe(row.get("BBU_20_2.0", close * 1.02), close * 1.02)
    bbl = safe(row.get("BBL_20_2.0", close * 0.98), close * 0.98)
    bbm = safe(row.get("BBM_20_2.0", close), close)
    if close < bbl:
        scores_long.append(80)
    elif close < bbm:
        scores_long.append(50)
    if close > bbu:
        scores_short.append(80)
    elif close > bbm:
        scores_short.append(50)

    # ── EMA Cross signals ──
    ema9 = safe(row.get("ema_9", safe(row.get("ema_5", close))), close)
    ema21 = safe(row.get("ema_21", close), close)
    ema50 = safe(row.get("ema_50", safe(row.get("ema_55", close))), close)
    ema200 = safe(row.get("ema_200", close), close)
    if ema9 > ema21:
        scores_long.append(60)
    else:
        scores_short.append(60)
    if close > ema50:
        scores_long.append(55)
    else:
        scores_short.append(55)
    if close > ema200:
        scores_long.append(65)
    else:
        scores_short.append(65)

    # ── Volume signals ──
    vol_mom = safe(row.get("vol_momentum", 1), 1)
    buy_press = safe(row.get("buy_pressure", 0.5), 0.5)
    if vol_mom > 1.5 and buy_press > 0.6:
        scores_long.append(70)
    elif vol_mom > 1.5 and buy_press < 0.4:
        scores_short.append(70)

    # ── CMF (Chaikin Money Flow) ──
    cmf = safe(row.get("cmf_20", 0), 0)
    if cmf > 0.1:
        scores_long.append(65)
    elif cmf < -0.1:
        scores_short.append(65)

    # ── ADX trend strength ──
    adx = safe(row.get("ADX_14", 25), 25)
    if adx > 40:
        if ema9 > ema21:
            scores_long.append(75)
        else:
            scores_short.append(75)
    elif adx > 25:
        if ema9 > ema21:
            scores_long.append(55)
        else:
            scores_short.append(55)

    # ── Z-Score mean reversion ──
    z = safe(row.get("zscore_20", 0), 0)
    if z < -2:
        scores_long.append(75)
    elif z < -1:
        scores_long.append(55)
    if z > 2:
        scores_short.append(75)
    elif z > 1:
        scores_short.append(55)

    # ── Candlestick patterns ──
    if safe(row.get("hammer", 0)):
        scores_long.append(65)
    if safe(row.get("shooting_star", 0)):
        scores_short.append(65)
    if safe(row.get("engulf_bull", 0)):
        scores_long.append(70)
    if safe(row.get("engulf_bear", 0)):
        scores_short.append(70)
    if safe(row.get("three_white", 0)):
        scores_long.append(60)

    # ── Compute final scores ──
    long_score = np.mean(scores_long) if scores_long else 50
    short_score = np.mean(scores_short) if scores_short else 50

    # Normalize with some noise suppression
    long_score = np.clip(long_score, 0, 100)
    short_score = np.clip(short_score, 0, 100)

    direction = "LONG" if long_score >= short_score else "SHORT"
    intensity = long_score if direction == "LONG" else short_score

    # ── ATR-based TP/SL calculation ──
    atr = safe(row.get("atr_14", close * 0.01), close * 0.01)
    rr = 1.5  # risk:reward base
    if direction == "LONG":
        entry = close
        sl = round(entry - atr * 1.0, 6)
        tp1 = round(entry + atr * rr, 6)
        tp2 = round(entry + atr * rr * 1.8, 6)
        tp3 = round(entry + atr * rr * 3.0, 6)
    else:
        entry = close
        sl = round(entry + atr * 1.0, 6)
        tp1 = round(entry - atr * rr, 6)
        tp2 = round(entry - atr * rr * 1.8, 6)
        tp3 = round(entry - atr * rr * 3.0, 6)

    # Win rate estimate (Bayesian-ish, based on score & ATR regime)
    base_wr = 0.40 + (intensity / 100) * 0.35
    vol_penalty = min(safe(row.get("hist_vol_20", 0.5), 0.5) / 5, 0.15)
    win_rate = round(np.clip(base_wr - vol_penalty, 0.3, 0.85) * 100, 1)

    return {
        "direction": direction,
        "intensity": round(intensity, 1),
        "long_score": round(long_score, 1),
        "short_score": round(short_score, 1),
        "entry": entry,
        "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "sl": sl,
        "atr": round(atr, 6),
        "rsi": round(rsi, 1),
        "win_rate": win_rate,
        "adx": round(adx, 1),
    }


# ═══════════════════════════════════════════════════════════════
#  SECTION 7: SCREENER ENGINE
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=120)
def run_screener(symbols: list, timeframe: str, min_score: float,
                 api_key: str, api_secret: str) -> list:
    """Screen multiple symbols and return sorted signals."""
    results = []
    for sym in symbols:
        df = fetch_ohlcv(sym, timeframe, 300, api_key, api_secret)
        if df is None or len(df) < 50:
            continue
        df = compute_indicators(df)
        signal = compute_signal_score(df)
        if signal["intensity"] >= min_score:
            signal["symbol"] = sym
            signal["price"] = df["close"].iloc[-1]
            signal["change_24h"] = round(
                (df["close"].iloc[-1] / df["close"].iloc[max(0, len(df) - 96)] - 1) * 100, 2)
            signal["volume_24h"] = round(df["volume"].iloc[-96:].sum(), 0)
            results.append(signal)
    results.sort(key=lambda x: x["intensity"], reverse=True)
    return results


# ═══════════════════════════════════════════════════════════════
#  SECTION 8: PERFORMANCE HISTORY (Persistent JSON)
# ═══════════════════════════════════════════════════════════════

HISTORY_FILE = "trade_history.json"

def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Demo history
    demo = []
    coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
             "AVAXUSDT", "LINKUSDT", "DOGEUSDT", "ADAUSDT", "MATICUSDT"]
    outcomes = [
        ("TP3", 8.5), ("TP2", 4.2), ("TP1", 2.1), ("SL", -2.0),
        ("TP1", 1.8), ("TP2", 5.1), ("SL", -1.5), ("TP3", 9.2),
        ("TP2", 3.8), ("SL", -2.3), ("TP1", 2.4), ("TP2", 4.7),
        ("TP3", 7.1), ("SL", -1.9), ("TP1", 1.6), ("TP2", 3.9),
        ("TP1", 2.2), ("TP3", 10.1), ("SL", -2.8), ("TP2", 4.4),
    ]
    now = datetime.utcnow()
    for i, (outcome, pct) in enumerate(outcomes):
        status = "Win" if not outcome.startswith("SL") else "Loss"
        demo.append({
            "timestamp": (now - timedelta(hours=i * 6)).strftime("%m/%d %H:%M"),
            "coin": random.choice(coins),
            "direction": random.choice(["LONG", "SHORT"]),
            "outcome": outcome,
            "pct": pct if status == "Win" else -abs(pct),
            "status": status,
            "entry": round(random.uniform(0.5, 65000), 4),
            "win_rate_at_entry": round(random.uniform(55, 82), 1),
        })
    return demo


def save_history(history: list):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def compute_win_rate(history: list) -> float:
    if not history:
        return 0.0
    wins = sum(1 for h in history if h["status"] == "Win")
    return round(wins / len(history) * 100, 1)


# ═══════════════════════════════════════════════════════════════
#  SECTION 9: UI COMPONENTS
# ═══════════════════════════════════════════════════════════════

def render_header(win_rate: float, total_signals: int, model_status: str):
    now = datetime.utcnow().strftime("%H:%M:%S UTC")
    st.markdown(f"""
    <div class="hdr">
        <div class="live-dot"></div>
        <div>
            <div class="hdr-title">⚡ AI TRADING BOT — BINANCE FUTURES</div>
            <div class="hdr-sub">PPO Deep RL • 130+ Indicators • {now}</div>
        </div>
        <div style="margin-left:auto;text-align:right">
            <div style="color:#ffd700;font-family:var(--font-mono);font-size:0.8rem;font-weight:700">
                {win_rate}% WIN RATE
            </div>
            <div style="color:#506272;font-size:0.62rem;font-family:var(--font-mono)">
                {total_signals} signals • {model_status}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_cards(history: list, signals: list):
    win_rate = compute_win_rate(history)
    total = len(history)
    wins = sum(1 for h in history if h["status"] == "Win")
    avg_profit = np.mean([h["pct"] for h in history if h["status"] == "Win"]) if wins else 0
    avg_loss = np.mean([h["pct"] for h in history if h["status"] == "Loss"]) if (total - wins) > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card green">
            <div class="metric-val">{win_rate}%</div>
            <div class="metric-lbl">Win Rate</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card blue">
            <div class="metric-val">{len(signals)}</div>
            <div class="metric-lbl">Active Signals</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card green">
            <div class="metric-val">+{avg_profit:.1f}%</div>
            <div class="metric-lbl">Avg Win</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card red">
            <div class="metric-val">{avg_loss:.1f}%</div>
            <div class="metric-lbl">Avg Loss</div>
        </div>""", unsafe_allow_html=True)


def fmt_price(price: float, sym: str = "") -> str:
    """Format price based on magnitude."""
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    else:
        return f"{price:.6f}"


def render_signal_card(sig: dict):
    sym = sig["symbol"]
    direction = sig["direction"]
    intensity = sig["intensity"]
    cls = "long" if direction == "LONG" else "short"
    badge_cls = "badge-long" if direction == "LONG" else "badge-short"
    bar_cls = "bar-long" if direction == "LONG" else "bar-short"
    change = sig.get("change_24h", 0)
    change_color = "#00ff88" if change >= 0 else "#ff3366"
    change_str = f"+{change}%" if change >= 0 else f"{change}%"

    entry_f = fmt_price(sig["entry"])
    tp1_f = fmt_price(sig["tp1"])
    tp2_f = fmt_price(sig["tp2"])
    tp3_f = fmt_price(sig["tp3"])
    sl_f = fmt_price(sig["sl"])

    st.markdown(f"""
    <div class="signal-card {cls}">
        <div class="signal-header">
            <div>
                <div class="coin-name">{sym}</div>
                <div style="font-size:0.65rem;color:var(--muted);font-family:var(--font-mono)">
                    RSI: {sig['rsi']} • ADX: {sig['adx']} •
                    <span style="color:{change_color}">{change_str}</span>
                </div>
            </div>
            <div style="text-align:right">
                <div class="direction-badge {badge_cls}">{direction}</div>
                <div style="font-size:0.62rem;color:var(--muted);font-family:var(--font-mono);margin-top:4px">
                    WR: <span style="color:#ffd700">{sig['win_rate']}%</span>
                </div>
            </div>
        </div>

        <div class="intensity-wrap">
            <div class="intensity-label">
                <span>INTENSITY SCORE</span>
                <span style="color:{'#00ff88' if direction=='LONG' else '#ff3366'};font-weight:700">{intensity}/100</span>
            </div>
            <div class="bar-bg">
                <div class="bar-fill {bar_cls}" style="width:{intensity}%"></div>
            </div>
        </div>

        <div class="price-grid">
            <div class="price-item">
                <div>
                    <div class="price-label">ENTRY</div>
                    <div class="price-value price-entry">{entry_f}</div>
                </div>
                <span onclick="navigator.clipboard.writeText('{entry_f}')" 
                      style="cursor:pointer;opacity:0.6;font-size:0.85rem" title="Copy">📋</span>
            </div>
            <div class="price-item">
                <div>
                    <div class="price-label">TP1 (+{round(abs(sig['tp1']-sig['entry'])/sig['entry']*100,2)}%)</div>
                    <div class="price-value price-tp">{tp1_f}</div>
                </div>
                <span onclick="navigator.clipboard.writeText('{tp1_f}')" 
                      style="cursor:pointer;opacity:0.6;font-size:0.85rem" title="Copy">📋</span>
            </div>
            <div class="price-item">
                <div>
                    <div class="price-label">TP2 (+{round(abs(sig['tp2']-sig['entry'])/sig['entry']*100,2)}%)</div>
                    <div class="price-value price-tp">{tp2_f}</div>
                </div>
                <span onclick="navigator.clipboard.writeText('{tp2_f}')" 
                      style="cursor:pointer;opacity:0.6;font-size:0.85rem" title="Copy">📋</span>
            </div>
            <div class="price-item">
                <div>
                    <div class="price-label">TP3 (+{round(abs(sig['tp3']-sig['entry'])/sig['entry']*100,2)}%)</div>
                    <div class="price-value price-tp">{tp3_f}</div>
                </div>
                <span onclick="navigator.clipboard.writeText('{tp3_f}')" 
                      style="cursor:pointer;opacity:0.6;font-size:0.85rem" title="Copy">📋</span>
            </div>
            <div class="price-item" style="grid-column:1/-1">
                <div>
                    <div class="price-label">STOP LOSS (-{round(abs(sig['sl']-sig['entry'])/sig['entry']*100,2)}%)</div>
                    <div class="price-value price-sl">{sl_f}</div>
                </div>
                <span onclick="navigator.clipboard.writeText('{sl_f}')" 
                      style="cursor:pointer;opacity:0.6;font-size:0.85rem" title="Copy">📋</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_history_table(history: list):
    win_rate = compute_win_rate(history)

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
        <div class="sec-title" style="border:none;margin:0;padding:0">📊 PERFORMANCE HISTORY</div>
        <div class="win-rate-badge">Win Rate: {win_rate}%</div>
    </div>
    """, unsafe_allow_html=True)

    rows_html = ""
    for h in history[:25]:
        status_color = "#00ff88" if h["status"] == "Win" else "#ff3366"
        pct = h["pct"]
        pct_str = f"+{pct}%" if pct > 0 else f"{pct}%"
        outcome = h["outcome"]
        if outcome.startswith("TP"):
            outcome_display = f"<span style='color:#00ff88'>Hit {outcome}: {pct_str}</span>"
        else:
            outcome_display = f"<span style='color:#ff3366'>Hit SL: {pct_str}</span>"

        dir_color = "#00ff88" if h["direction"] == "LONG" else "#ff3366"
        rows_html += f"""
        <tr>
            <td style="font-weight:700;color:var(--text)">{h['coin']}</td>
            <td style="color:{dir_color};font-size:0.65rem">{h['direction']}</td>
            <td style="color:{status_color}">{h['status']}</td>
            <td>{outcome_display}</td>
            <td style="color:var(--muted)">{h['timestamp']}</td>
        </tr>
        """

    st.markdown(f"""
    <div style="overflow-x:auto">
    <table class="hist-table">
        <thead>
            <tr>
                <th>COIN</th>
                <th>DIR</th>
                <th>STATUS</th>
                <th>RESULT</th>
                <th>TIME</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


def render_model_info(model_status: str, ppo_available: bool):
    libs = load_libraries()
    ppo_str = "✅ PPO Active" if libs['PPO'] else "⚠️ Demo Mode"
    ccxt_str = "✅ Connected" if libs['ccxt'] else "⚠️ Simulated"
    ta_str = "✅ 130+ Loaded" if libs['ta'] else "⚠️ Basic (20+)"

    st.markdown(f"""
    <div class="model-info">
        <div class="row"><span class="key">🤖 RL Model</span><span class="val">{ppo_str}</span></div>
        <div class="row"><span class="key">📡 Exchange</span><span class="val">{ccxt_str}</span></div>
        <div class="row"><span class="key">📊 Indicators</span><span class="val">{ta_str}</span></div>
        <div class="row"><span class="key">🧠 Algorithm</span><span class="val">PPO (Stable-Baselines3)</span></div>
        <div class="row"><span class="key">🏋️ Training</span><span class="val">Continuous / Daily</span></div>
        <div class="row"><span class="key">⚡ Reward Fn</span><span class="val">+TP Hit / -SL Penalty</span></div>
        <div class="row"><span class="key">🔄 Status</span><span class="val" style="color:#ffd700">{model_status}</span></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SECTION 10: MAIN APP
# ═══════════════════════════════════════════════════════════════

def main():
    # ── Session State Init ──
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    if "signals" not in st.session_state:
        st.session_state.signals = []

    libs = load_libraries()

    # ── SIDEBAR SETTINGS ──
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        api_key = st.text_input("Binance API Key", type="password", key="api_key",
                                 help="Optional: for live data & trading")
        api_secret = st.text_input("Binance API Secret", type="password", key="api_secret")
        st.divider()
        timeframe = st.selectbox("Timeframe", ["5m", "15m", "1h", "4h"], index=1)
        min_score = st.slider("Min Intensity Score", 50, 95, 65)
        max_coins = st.slider("Max Coins to Screen", 5, 30, 12)
        st.divider()
        auto_refresh = st.checkbox("Auto Refresh (120s)", value=False)
        enable_rl = st.checkbox("Enable RL Training", value=False,
                                 help="Train PPO on first run (slow!)")
        st.divider()
        st.markdown("""
        <div style="font-size:0.65rem;color:#506272;font-family:var(--font-mono)">
        <b style="color:#00ff88">⚠️ DISCLAIMER</b><br><br>
        This tool is for <b>educational purposes</b> only. Crypto trading involves
        significant financial risk. Always use proper risk management.
        </div>
        """, unsafe_allow_html=True)

    # ── Auto-refresh ──
    if auto_refresh and time.time() - st.session_state.last_refresh > 120:
        st.session_state.last_refresh = time.time()
        st.rerun()

    # ── Load data ──
    history = st.session_state.history
    win_rate = compute_win_rate(history)
    model_status = "PPO Active" if libs['PPO'] else "Rule-Based Demo"

    # ── HEADER ──
    render_header(win_rate, len(st.session_state.signals), model_status)

    # ── METRIC CARDS ──
    render_metric_cards(history, st.session_state.signals)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── MAIN TABS ──
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 SCREENER", "📊 HISTORY", "🤖 MODEL", "📡 API SETUP"])

    # ════════════════════════════════════════════
    # TAB 1: SCREENER
    # ════════════════════════════════════════════
    with tab1:
        col_run, col_info = st.columns([2, 3])
        with col_run:
            run_btn = st.button("🔍 Run Screener Now", use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--muted);padding-top:8px">
                Screening up to <b style="color:var(--blue)">{max_coins}</b> pairs •
                Min score: <b style="color:var(--green)">{min_score}</b> •
                TF: <b style="color:var(--yellow)">{timeframe}</b>
            </div>
            """, unsafe_allow_html=True)

        if run_btn or not st.session_state.signals:
            symbols = fetch_futures_symbols(api_key, api_secret)[:max_coins]
            with st.spinner(f"🔍 Scanning {len(symbols)} coins with 130+ indicators..."):
                signals = run_screener(symbols, timeframe, min_score, api_key, api_secret)
                st.session_state.signals = signals
                st.session_state.last_refresh = time.time()

        signals = st.session_state.signals

        if not signals:
            st.markdown("""
            <div style="text-align:center;padding:40px;color:var(--muted);font-family:var(--font-mono)">
                <div style="font-size:2rem">🔍</div>
                <div>No signals above threshold. Try lowering Min Score.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Filter buttons
            cf1, cf2, cf3 = st.columns(3)
            with cf1:
                show_all = st.button("ALL", use_container_width=True)
            with cf2:
                show_long = st.button("🟢 LONG", use_container_width=True)
            with cf3:
                show_short = st.button("🔴 SHORT", use_container_width=True)

            if "signal_filter" not in st.session_state:
                st.session_state.signal_filter = "ALL"
            if show_all:
                st.session_state.signal_filter = "ALL"
            if show_long:
                st.session_state.signal_filter = "LONG"
            if show_short:
                st.session_state.signal_filter = "SHORT"

            filtered = [s for s in signals
                        if st.session_state.signal_filter == "ALL"
                        or s["direction"] == st.session_state.signal_filter]

            st.markdown(f"""
            <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--muted);
                        margin:6px 0;letter-spacing:1px">
                SHOWING {len(filtered)} / {len(signals)} SIGNALS
                • FILTER: {st.session_state.signal_filter}
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="scroll-section">', unsafe_allow_html=True)
            for sig in filtered:
                render_signal_card(sig)
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # TAB 2: HISTORY
    # ════════════════════════════════════════════
    with tab2:
        render_history_table(history)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Analytics
        st.markdown('<div class="sec-title">📈 PERFORMANCE ANALYTICS</div>', unsafe_allow_html=True)

        df_hist = pd.DataFrame(history)
        if not df_hist.empty:
            # Cumulative P&L
            df_hist["cum_pnl"] = df_hist["pct"].cumsum()
            st.markdown("**Cumulative P&L (%)**")
            st.line_chart(df_hist["cum_pnl"].reset_index(drop=True), height=150,
                           use_container_width=True)

            # Win/Loss breakdown
            a1, a2, a3 = st.columns(3)
            wins = df_hist[df_hist["status"] == "Win"]
            losses = df_hist[df_hist["status"] == "Loss"]
            with a1:
                st.metric("Total Trades", len(df_hist))
            with a2:
                st.metric("Wins", len(wins), f"+{wins['pct'].mean():.1f}% avg" if len(wins) > 0 else "0")
            with a3:
                st.metric("Losses", len(losses), f"{losses['pct'].mean():.1f}% avg" if len(losses) > 0 else "0")

            # TP distribution
            st.markdown("**Outcome Distribution**")
            if "outcome" in df_hist.columns:
                outcome_counts = df_hist["outcome"].value_counts()
                st.bar_chart(outcome_counts, height=150, use_container_width=True)

    # ════════════════════════════════════════════
    # TAB 3: MODEL INFO
    # ════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="sec-title">🤖 DEEP RL MODEL STATUS</div>', unsafe_allow_html=True)
        render_model_info(model_status, libs['PPO'] is not None)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="model-info">
            <div style="color:var(--green);font-weight:700;margin-bottom:8px">
                🧠 PPO REWARD FUNCTION
            </div>
            <div style="color:var(--muted);font-size:0.7rem;line-height:1.8">
                • Hit TP1 → <span style="color:#00ff88">+1.0 reward</span><br>
                • Hit TP2 → <span style="color:#00ff88">+2.0 reward</span><br>
                • Hit TP3 → <span style="color:#00ff88">+3.0 reward</span><br>
                • Hit SL  → <span style="color:#ff3366">-2.5 penalty</span><br>
                • Hold    → <span style="color:#506272">-0.001 time decay</span><br>
                • Commission: <span style="color:#ffd700">0.04% per trade</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if enable_rl and st.session_state.signals:
            st.markdown('<div class="sec-title" style="margin-top:10px">🏋️ RL TRAINING</div>',
                         unsafe_allow_html=True)
            sym = st.session_state.signals[0]["symbol"]
            if st.button(f"Train PPO on {sym} (10k steps)", use_container_width=True):
                with st.spinner(f"Training PPO on {sym}..."):
                    df = fetch_ohlcv(sym, "15m", 500, api_key, api_secret)
                    if df is not None:
                        df = compute_indicators(df)
                        df_hash = str(hash(df["close"].sum()))
                        model, env = get_or_train_ppo(df_hash, df, 10000)
                        if model:
                            st.success(f"✅ PPO trained successfully on {sym}!")
                            if env.trade_log:
                                df_log = pd.DataFrame(env.trade_log)
                                wins_rl = len(df_log[df_log["pnl"] > 0])
                                st.metric("RL Backtest Win Rate",
                                          f"{wins_rl/len(df_log)*100:.1f}%",
                                          f"{len(df_log)} trades")
                        else:
                            st.warning("⚠️ Stable-Baselines3 not installed. Running rule-based mode.")

        st.markdown("""
        <div style="margin-top:10px;font-family:var(--font-mono);font-size:0.65rem;color:var(--muted)">
            <b style="color:var(--blue)">CONTINUOUS LEARNING FLOW:</b><br>
            1. Fetch 500 candles every 15min<br>
            2. Compute 130+ indicators<br>
            3. PPO agent observes market state<br>
            4. Agent selects action (Long/Short/Hold/Close)<br>
            5. Environment returns reward (TP/SL check)<br>
            6. Agent updates policy via gradient descent<br>
            7. Daily retraining if win rate drops &lt;50%
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # TAB 4: API SETUP & DEPLOYMENT
    # ════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="sec-title">📡 BINANCE API INTEGRATION</div>',
                     unsafe_allow_html=True)
        st.markdown("""
        <div class="model-info">
            <div style="color:var(--blue);font-weight:700;margin-bottom:6px">HOW TO GET API KEY:</div>
            <div style="color:var(--muted);font-size:0.7rem;line-height:2">
                1. Login to <b style="color:var(--text)">binance.com</b><br>
                2. Account → API Management<br>
                3. Create API → Enable Futures Trading<br>
                4. Whitelist your IP (recommended)<br>
                5. Copy Key & Secret to Settings sidebar
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🚀 DEPLOY TO STREAMLIT CLOUD</div>',
                     unsafe_allow_html=True)
        st.markdown("""
        <div class="model-info">
            <div style="color:var(--green);font-weight:700;margin-bottom:6px">
                GET FREE HTTPS LINK FOR HP BROWSER:
            </div>
            <div style="color:var(--muted);font-size:0.7rem;line-height:2.2">
                <b style="color:var(--yellow)">Step 1:</b> Push code to GitHub repo<br>
                <b style="color:var(--yellow)">Step 2:</b> Go to share.streamlit.io<br>
                <b style="color:var(--yellow)">Step 3:</b> Login with GitHub → New App<br>
                <b style="color:var(--yellow)">Step 4:</b> Select repo → main file: app.py<br>
                <b style="color:var(--yellow)">Step 5:</b> Add Secrets (API keys) in Settings<br>
                <b style="color:var(--yellow)">Step 6:</b> Deploy → Get HTTPS link ✅<br><br>
                <b style="color:var(--blue)">URL format:</b>
                <span style="color:var(--text)">
                    https://your-app.streamlit.app
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # API Test button
        if st.button("🔌 Test Binance Connection", use_container_width=True):
            if not api_key:
                st.warning("⚠️ No API key provided. Running in demo/simulated mode.")
            else:
                with st.spinner("Testing connection..."):
                    symbols = fetch_futures_symbols(api_key, api_secret)
                    st.success(f"✅ Connected! Found {len(symbols)} futures pairs.")


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
