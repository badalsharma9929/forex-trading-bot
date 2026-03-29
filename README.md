# Forex Trading Bot - Paper Trading

A complete forex trading bot with AI/ML capabilities, sentiment analysis, and paper trading simulation.

## Features

- **Technical Analysis**: RSI, MACD, Bollinger Bands, EMA, ADX, Stochastic, CCI, ATR
- **Sentiment Analysis**: FinBERT for news-based sentiment
- **ML Models**: Random Forest, XGBoost, LSTM
- **Risk Management**: Position sizing, stop-loss, kill switch, drawdown limits
- **Paper Trading**: Virtual ₹100,000 starting balance
- **Dashboard**: Streamlit web interface with real-time charts

## Tech Stack (100% Free)

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Data | Free APIs (no key required) |
| ML | scikit-learn, TensorFlow |
| Dashboard | Streamlit |
| Database | SQLite |

## Installation

```bash
cd forex-trading-bot
pip install -r requirements.txt
```

## Usage

### Start Dashboard
```bash
streamlit run monitoring/dashboard.py
```

### Run Bot
```bash
python main.py
```

### Test Individual Components
```bash
python data/collectors/price_collector.py
python data/collectors/news_collector.py
python strategies/indicators.py
python sentiment/analyzer.py
python risk/manager.py
```

## Project Structure

```
forex-trading-bot/
├── config/              # Configuration
├── data/
│   ├── collectors/      # Data collection
│   └── database/        # SQLite schema
├── strategies/          # Trading strategies & ML
├── sentiment/           # Sentiment analysis
├── risk/                # Risk management
├── paper_trading/       # Trading simulator
├── monitoring/          # Dashboard
└── main.py              # Bot orchestrator
```

## Trading Pairs (India Compliant)

- USD/INR
- EUR/INR
- GBP/INR
- JPY/INR

## Risk Management

- Max 2% risk per trade
- Max 10% position size
- 20% max drawdown (kill switch)
- 5% daily loss limit
- 5 consecutive losses stop

## Disclaimer

This is for **PAPER TRADING ONLY**. Not financial advice. Use at your own risk.
