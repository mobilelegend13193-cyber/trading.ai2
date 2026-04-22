# 🤖 AI Trading Bot — Binance Futures
### Deep Reinforcement Learning Screener & Dashboard

---

## 📁 Project Structure

```
trading_bot/
├── app.py                          # Main Streamlit application
├── requirements.txt                # All Python dependencies
├── .streamlit/
│   ├── config.toml                 # Theme & server config
│   └── secrets.toml.template       # API keys template (DON'T commit real keys)
└── README.md                       # This file
```

---

## 🚀 DEPLOY TO STREAMLIT CLOUD (Free HTTPS for HP Browser)

### Step 1: Push to GitHub
```bash
# Install git if needed
git init
git add .
git commit -m "AI Trading Bot v1.0"
git remote add origin https://github.com/USERNAME/trading-bot.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. Login with your GitHub account
3. Click **"New app"**
4. Select:
   - **Repository**: `USERNAME/trading-bot`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Advanced settings"** → Add secrets:
   ```toml
   [binance]
   api_key = "YOUR_API_KEY"
   api_secret = "YOUR_API_SECRET"
   ```
6. Click **"Deploy!"**
7. ✅ Get your free HTTPS link: `https://username-trading-bot.streamlit.app`

---

## 💻 LOCAL INSTALLATION

### Prerequisites
- Python 3.10+ 
- pip

### Install & Run
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Open in browser: http://localhost:8501
```

---

## 🤖 ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT DASHBOARD                    │
│  Mobile-First UI • Dark Terminal Theme • Copy Buttons   │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────▼──────────┐           ┌──────────▼──────────┐
│   CCXT CONNECTOR   │           │   SCREENER ENGINE   │
│  Binance Futures   │           │  130+ Indicators    │
│  Live OHLCV Data   │           │  0-100 Score System │
└─────────┬──────────┘           └──────────┬──────────┘
          │                                 │
          └────────────────┬────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  RL ENGINE (PPO)                         │
│  State: 130+ normalized indicators (20-bar window)       │
│  Action: Long / Short / Hold / Close                    │
│  Reward: +TP Hit / -SL Penalty / -Time Decay            │
│  Policy: Multi-Layer Perceptron (Stable-Baselines3)     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│              SIGNAL OUTPUT & HISTORY                     │
│  Entry | TP1 | TP2 | TP3 | SL (Copy-Ready 📋)          │
│  Win Rate Tracking | P&L History | Outcome Analysis     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 TECHNICAL INDICATORS (130+)

| Category | Indicators |
|----------|-----------|
| **Moving Averages** | EMA 5/8/13/21/34/55/89/144/200, SMA 10/20/50/100/200, WMA, HMA, VWMA |
| **Oscillators** | RSI 7/14/21, MACD, Stochastic, CCI, MFI, Williams %R, ROC, Momentum, CMO, PPO, DPO, TSI |
| **Volatility** | Bollinger Bands, Keltner Channel, ATR 7/14, NATR, True Range, UI, Mass Index |
| **Volume** | OBV, Accumulation/Distribution, ADOSC, CMF, EOM, PVT, NVI, PVI, VWAP, KVO |
| **Trend** | ADX, Aroon, Ichimoku, PSAR, SuperTrend, CKSP, TTM Trend, Qstick, Vortex |
| **Candlestick** | Doji, Hammer, Shooting Star, Engulfing (Bull/Bear), Three White Soldiers |
| **Order Flow** | Buy/Sell Pressure, Delta Volume, Cumulative Delta, Volume Momentum, Market Impact |
| **Statistical** | Z-Score, Percentile Rank, Variance, Skewness, Kurtosis, Historical Vol, Realized Vol |

---

## 🔑 BINANCE API SETUP

1. Login to **binance.com**
2. Account → **API Management** → Create API
3. Enable: ✅ Futures Trading ✅ Read Info
4. (Optional) Whitelist your IP for security
5. Copy **API Key** and **Secret Key**
6. Add to Streamlit Cloud secrets or sidebar

> ⚠️ **Never share your API keys or commit them to GitHub!**

---

## 📱 MOBILE USAGE TIPS

- Open the HTTPS link in Chrome/Safari on your phone
- **Landscape mode** recommended for signal cards
- Tap **📋** next to any price to copy it
- Use **Auto Refresh** checkbox for 120s live updates
- Save the link to Home Screen as a PWA

---

## ⚠️ DISCLAIMER

This software is for **educational and research purposes only**. 
- It does NOT guarantee profits
- Crypto trading involves substantial financial risk
- Past performance does not indicate future results
- Always use proper position sizing and risk management
- Never trade with money you cannot afford to lose

---

## 📦 DEPENDENCIES

| Library | Purpose |
|---------|---------|
| `streamlit` | Web dashboard framework |
| `ccxt` | Binance Futures API connection |
| `pandas-ta` | 130+ technical indicators |
| `stable-baselines3` | PPO Reinforcement Learning |
| `gymnasium` | RL environment standard |
| `torch` | Neural network backend |
| `pandas` / `numpy` | Data processing |
