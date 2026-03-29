# Forex Trading Bot - Technical Documentation

## Overview
A comprehensive forex trading bot with AI/ML capabilities, sentiment analysis, and paper trading simulation. Built with 100% free tools and APIs.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Language** | Python 3.10+ | Core programming language |
| **Data** | Pandas, NumPy | Data manipulation |
| **Database** | SQLite | Local data storage |
| **APIs** | Frankfurter API, ExchangeRate-API | Free forex data (no keys) |
| **ML** | scikit-learn, XGBoost, TensorFlow | Machine learning models |
| **NLP** | Transformers (FinBERT), NLTK | Sentiment analysis |
| **Dashboard** | Streamlit, Plotly | Web UI & visualization |
| **Version Control** | Git, GitHub | Code management |

---

## 📊 Phases of Implementation

### Phase 1: Foundation & Data Pipeline
- Project structure setup
- SQLite database initialization
- Free API integration (price data)
- Data collection pipeline

### Phase 2: Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- EMA/SMA (Exponential/Simple Moving Averages)
- ADX (Average Directional Index)
- Stochastic Oscillator
- CCI (Commodity Channel Index)
- ATR (Average True Range)

### Phase 3: Sentiment Analysis
- News collection
- FinBERT sentiment analysis
- Signal generation from news

### Phase 4: Machine Learning
- Feature engineering
- Random Forest Classifier
- XGBoost
- LSTM Neural Network
- Ensemble predictions

### Phase 5: Risk Management
- Position sizing (Kelly Criterion)
- Stop-loss / Take-profit
- Kill switch mechanisms
- Drawdown limits

### Phase 6: Paper Trading
- Virtual trade execution
- P&L tracking
- Trade history

### Phase 7: Dashboard & Deployment
- Streamlit web interface
- Real-time charts
- GitHub deployment

---

## 🤖 AI & ML Techniques Used

### 1. Machine Learning Models

#### Random Forest Classifier
```
Purpose: Predict price direction (up/down)
Algorithm: Ensemble of decision trees
Features: 19 technical indicators
```

#### XGBoost
```
Purpose: Enhanced price prediction
Algorithm: Gradient boosting
Advantage: Handles missing values, regularization
```

#### LSTM Neural Network
```
Purpose: Time series forecasting
Architecture: Long Short-Term Memory
Input: Sequential price data
Layers: 2 LSTM + Dropout + Dense
```

### 2. Natural Language Processing

#### FinBERT (Finance BERT)
```
Purpose: Finance-specific sentiment analysis
Model: prosusai/finbert
Input: News headlines & descriptions
Output: positive/negative/neutral
```

#### VADER (Fallback)
```
Purpose: General sentiment analysis
Library: NLTK
Use Case: Quick sentiment scoring
```

### 3. Technical Analysis Algorithms

| Algorithm | Formula | Signal |
|-----------|---------|--------|
| **RSI** | 100 - (100 / (1 + RS)) | <30 Buy, >70 Sell |
| **MACD** | EMA12 - EMA26 | Signal line crossover |
| **Bollinger Bands** | MA ± 2σ | Price touches bands |
| **ADX** | Smoothed DX | >25 strong trend |

---

## 📈 Trading Signals Generation

### Technical Signal Logic
```
BUY Signal:
  - RSI < 30 (Oversold)
  - Price < Lower Bollinger Band
  - MACD Histogram > 0
  
SELL Signal:
  - RSI > 70 (Overbought)
  - Price > Upper Bollinger Band
  - MACD Histogram < 0
```

### Sentiment Signal Logic
```
Score > 0.2 → BULLISH
Score < -0.2 → BEARISH
Otherwise → NEUTRAL
```

### Combined Signal
```
Probability UP = 50% + (Technical Score × 15%) + (Sentiment Score × 25%)
```

---

## 🗂️ Project Structure

```
forex-trading-bot/
├── config/
│   ├── api_keys.py        # API key placeholders
│   ├── free_apis.py       # Free API endpoints
│   └── settings.py         # Configuration
├── data/
│   ├── collectors/
│   │   ├── price_collector.py   # Price data
│   │   └── news_collector.py    # News data
│   └── database/
│       ├── schema.py       # DB tables
│       └── queries.py      # DB utilities
├── strategies/
│   ├── indicators.py      # Technical indicators
│   ├── rule_based.py      # Trading rules
│   └── ml_model.py        # ML predictions
├── sentiment/
│   └── analyzer.py        # FinBERT + VADER
├── risk/
│   └── manager.py         # Risk management
├── paper_trading/
│   └── simulator.py       # Trade execution
├── monitoring/
│   └── dashboard.py       # Streamlit UI
└── main.py                # Bot orchestrator
```

---

## 📊 Database Schema

### Tables
1. **price_data** - OHLCV price data
2. **news_data** - News articles
3. **trades** - Trade history
4. **account** - Account balance & metrics
5. **indicators** - Calculated indicators
6. **ml_predictions** - Model predictions
7. **sentiment_data** - Sentiment scores

---

## 🚀 Deployment

### Local
```bash
pip install -r requirements.txt
streamlit run monitoring/dashboard.py
```

### GitHub + Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy automatically

---

## 📋 APIs Used (Free, No Keys)

| API | Purpose | Limit |
|-----|---------|-------|
| Frankfurter | Exchange rates | Unlimited |
| ExchangeRate-API | Backup rates | Unlimited |
| HuggingFace | FinBERT model | Free |

---

## ⚠️ Disclaimer

This bot is for **PAPER TRADING ONLY**. Not financial advice. Use at your own risk.

---

## 📚 References

- [scikit-learn Documentation](https://scikit-learn.org/)
- [TensorFlow Keras](https://tensorflow.org)
- [HuggingFace Transformers](https://huggingface.co/)
- [Streamlit Documentation](https://streamlit.io/)
- [TA-Lib Python](https://github.com/mrjbq7/ta-lib)
