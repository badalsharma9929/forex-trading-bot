# Forex Trading Bot - Paper Trading

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Live Dashboard**: https://forex-trading-bot-jhvewmfrnsjwxawihzksx2.streamlit.app/

A complete forex trading bot with AI/ML capabilities, sentiment analysis, and paper trading simulation. Built with 100% free APIs - no API keys required!

---

## Features

- **Technical Analysis**: RSI, MACD, Bollinger Bands, EMA, ADX, Stochastic, CCI, ATR
- **Sentiment Analysis**: VADER for news-based sentiment analysis
- **ML Models**: Random Forest, XGBoost framework ready
- **Risk Management**: Position sizing, stop-loss, kill switch, drawdown limits
- **Paper Trading**: Virtual ₹100,000 starting balance
- **Dashboard**: Streamlit web interface with real-time charts

---

## Quick Start

### 1. Use the Live App (No Installation)

Visit: **https://forex-trading-bot-jhvewmfrnsjwxawihzksx2.streamlit.app/**

### 2. Run Locally

```bash
# Clone the repository
git clone https://github.com/badalsharma9929/forex-trading-bot.git
cd forex-trading-bot

# Install dependencies
pip install -r requirements.txt

# Start the dashboard
streamlit run streamlit_app.py

# Or run the full bot
python main.py
```

---

## How to Use the App

### Dashboard Overview

The dashboard has 3 main sections:

1. **Price Chart** (Left) - Live candlestick chart with technical indicators
2. **Trading Panel** (Middle) - Buy/Sell buttons with signal probability
3. **News Sentiment** (Right) - Real-time news analysis

### Placing Trades

1. Select your currency pair (USD/INR, EUR/INR, GBP/INR, JPY/INR)
2. View the signal probability (UP% / DOWN%)
3. Enter position size (100-10,000 units)
4. Click **BUY** or **SELL** button
5. Monitor your open position and P&L
6. Click **CLOSE** to exit the trade

### Understanding Signals

- **🟢 STRONG BUY** (65%+ probability) - High confidence upward signal
- **🟢 BUY** (55%+ probability) - Moderate upward signal
- **🟡 HOLD** - Neutral market conditions
- **🔴 SELL** (55%+ probability) - Moderate downward signal
- **🔴 STRONG SELL** (65%+ probability) - High confidence downward signal

### Technical Indicators

| Indicator | Description | Signal |
|-----------|-------------|--------|
| RSI | Relative Strength Index | <30 oversold, >70 overbought |
| MACD | Moving Average Convergence | Positive = bullish, Negative = bearish |
| Bollinger Bands | Price volatility bands | Lower band = support, Upper = resistance |
| EMA | Exponential Moving Average | Price above = bullish trend |

---

## Tech Stack (100% Free)

| Component | Technology | Cost |
|-----------|-------------|------|
| Language | Python 3.10+ | Free |
| Price Data | Frankfurter API | Free |
| News Data | Sample forex news | Free |
| Sentiment | VADER (NLTK) | Free |
| Dashboard | Streamlit | Free |
| Database | SQLite | Free |
| Deployment | Streamlit Cloud | Free |

---

## Project Structure

```
forex-trading-bot/
├── streamlit_app.py           # Streamlit Cloud entry point
├── main.py                   # Bot orchestrator
├── requirements.txt          # Dependencies
├── config/
│   ├── settings.py          # Configuration
│   └── free_apis.py         # API endpoints
├── data/
│   ├── collectors/
│   │   ├── price_collector.py    # Price data (Frankfurter API)
│   │   └── news_collector.py    # News collector
│   └── database/
│       ├── schema.py             # SQLite tables
│       └── queries.py            # Database utilities
├── strategies/
│   ├── indicators.py            # Technical analysis
│   ├── rule_based.py            # Rule-based strategy
│   └── ml_model.py             # ML models
├── sentiment/
│   └── analyzer.py              # VADER sentiment
├── risk/
│   └── manager.py              # Risk management
├── paper_trading/
│   └── simulator.py            # Paper trading simulator
└── monitoring/
    └── dashboard.py            # Streamlit dashboard
```

---

## Risk Management

The bot includes robust risk management:

- **Max 2% risk per trade** - Limits losses on single trades
- **Max 10% position size** - Prevents over-concentration
- **20% max drawdown** - Kill switch when losses exceed 20%
- **5% daily loss limit** - Auto-stops daily trading
- **5 consecutive losses** - Auto-stop after 5 losses in a row
- **Emergency Stop** - Manual kill switch button

---

## Trading Pairs (India Compliant)

- USD/INR - US Dollar / Indian Rupee
- EUR/INR - Euro / Indian Rupee
- GBP/INR - British Pound / Indian Rupee
- JPY/INR - Japanese Yen / Indian Rupee

---

## Deployment

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repository: `badalsharma9929/forex-trading-bot`
5. Branch: `master`
6. Main file: `streamlit_app.py`
7. Click **Deploy!**

### Local Deployment

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

---

## Disclaimer

⚠️ **IMPORTANT**: This is for **PAPER TRADING ONLY**.

- No real money is involved
- Virtual ₹100,000 starting balance
- Not financial advice
- Past performance does not guarantee future results
- Trade at your own risk

---

## License

MIT License - feel free to use, modify, and distribute.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Support

For issues or questions, please open an issue on GitHub.
