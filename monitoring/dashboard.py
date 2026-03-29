"""
Forex Trading Bot - Dashboard
New UI with Trading & Sentiment Features
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database.schema import init_database
from data.collectors.price_collector import FreePriceCollector
from data.collectors.news_collector import FreeNewsCollector
from risk.manager import RiskManager
from paper_trading.simulator import PaperTradingSimulator
from strategies.indicators import TechnicalIndicators
from sentiment.analyzer import SentimentAnalyzer


def init_session():
    if 'init' not in st.session_state:
        init_database()
        st.session_state.price_collector = FreePriceCollector()
        st.session_state.news_collector = FreeNewsCollector()
        st.session_state.risk_manager = RiskManager()
        st.session_state.simulator = PaperTradingSimulator()
        st.session_state.sentiment_analyzer = SentimentAnalyzer()
        st.session_state.init = True


def price_chart(df, pair):
    if df.empty:
        st.warning("No data")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=pair
    ))
    
    if 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_upper'],
            line=dict(color='red', width=1, dash='dash'), name='BB Upper'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_lower'],
            line=dict(color='green', width=1, dash='dash'), name='BB Lower'))
    
    if 'ema_12' in df.columns:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ema_12'],
            line=dict(color='blue', width=1.5), name='EMA 12'))
    
    fig.update_layout(height=350, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="Forex Trading Bot", page_icon="📈", layout="wide")
    init_session()
    
    st.markdown("""
    <style>
    .main-header {font-size:2rem; font-weight:bold; color:#1f77b4;}
    .metric-box {background:#262730; padding:15px; border-radius:10px; text-align:center;}
    .trade-btn-buy {background:#28a745; color:white; padding:15px 30px; font-size:1.2rem; border:none; border-radius:8px; width:100%;}
    .trade-btn-sell {background:#dc3545; color:white; padding:15px 30px; font-size:1.2rem; border:none; border-radius:8px; width:100%;}
    .signal-box {background:#1e1e1e; padding:20px; border-radius:10px; border:2px solid #444;}
    .news-card {background:#262730; padding:12px; margin:8px 0; border-radius:8px; border-left:4px solid #1f77b4;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-header">📈 Forex Trading Bot - Dashboard</p>', unsafe_allow_html=True)
    st.caption("Paper Trading Mode | ₹1,00,000 Virtual Balance")
    
    # Top metrics row
    account = st.session_state.risk_manager.get_account_info()
    metrics = st.session_state.risk_manager.get_performance_metrics()
    stats = st.session_state.simulator.get_statistics()
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("💰 Balance", f"₹{account['balance']:,.0f}")
    with m2:
        clr = "normal" if metrics['total_pnl'] >= 0 else "inverse"
        st.metric("📊 P&L", f"₹{metrics['total_pnl']:,.0f}", f"{metrics['total_pnl_percentage']:.1f}%", delta_color=clr)
    with m3:
        st.metric("🎯 Win Rate", f"{metrics['win_rate']:.1f}%", f"{stats['winning_trades']}W-{stats['losing_trades']}L")
    with m4:
        status = "🟢 Active" if not metrics['is_halted'] else "🔴 Stopped"
        st.metric("⚡ Status", status)
    with m5:
        st.metric("📋 Total Trades", stats['total_trades'])
    
    st.divider()
    
    # Main content - 3 columns
    left, mid, right = st.columns([1.2, 1, 1])
    
    # ========== LEFT: Chart ==========
    with left:
        st.subheader("📊 Price Chart")
        pair = st.selectbox("Currency Pair", ["USD/INR", "EUR/INR", "GBP/INR", "JPY/INR"])
        
        df = st.session_state.price_collector.get_ohlcv(pair.replace("/", ""), periods=100)
        df_ind = TechnicalIndicators.calculate_all(df)
        price_chart(df_ind, pair)
        
        # Indicators
        if not df_ind.empty:
            latest = df_ind.iloc[-1]
            rsi = latest.get('rsi_14', 50)
            macd = latest.get('macd_histogram', 0)
            bb_pos = latest.get('bb_position', 0.5)
            
            i1, i2, i3 = st.columns(3)
            with i1:
                rsi_clr = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
                st.metric("RSI", f"{rsi:.0f}", rsi_clr)
            with i2:
                macd_clr = "🟢" if macd > 0 else "🔴"
                st.metric("MACD", f"{macd:.4f}", macd_clr)
            with i3:
                st.metric("BB Pos", f"{bb_pos:.2f}")
            
            curr = st.session_state.price_collector.get_latest_price(pair.replace("/", ""))
            if curr.get('success'):
                st.success(f"Current: ₹{curr['rate']:.4f}")
    
    # ========== MIDDLE: Trading & Signals ==========
    with mid:
        st.subheader("💹 Trade Panel")
        
        current_price = st.session_state.price_collector.get_latest_price(pair.replace("/", ""))
        price_val = current_price.get('rate', 0) if current_price.get('success') else 0
        
        has_pos = st.session_state.simulator.has_open_position()
        open_pos = st.session_state.simulator.get_open_position()
        
        if has_pos and open_pos:
            st.warning(f"📌 **Open Position**\n\n{open_pos['direction']} @ ₹{open_pos['entry_price']:.4f}\n\nSize: {open_pos['position_size']} units")
            
            if current_price.get('success'):
                if open_pos['direction'] == 'BUY':
                    pnl = (price_val - open_pos['entry_price']) * open_pos['position_size']
                else:
                    pnl = (open_pos['entry_price'] - price_val) * open_pos['position_size']
                clr = "green" if pnl >= 0 else "red"
                st.markdown(f"**P&L:** :{clr}[₹{pnl:.2f}]")
            
            if st.button("📤 CLOSE", type="primary", use_container_width=True):
                result = st.session_state.simulator.close_position(exit_price=price_val, reason="Manual")
                if result.get('success'):
                    st.session_state.risk_manager.update_after_trade(result['trade_result'])
                    st.success(f"Closed! P&L: ₹{result['trade_result']['pnl']:.2f}")
                    st.rerun()
        else:
            size = st.number_input("Position Size", min_value=100, max_value=10000, value=1000, step=100)
            
            # Calculate signals
            technical_score = 0
            if rsi < 30: technical_score += 1
            elif rsi > 70: technical_score -= 1
            if macd > 0: technical_score += 1
            else: technical_score -= 1
            if bb_pos < 0.2: technical_score += 1
            elif bb_pos > 0.8: technical_score -= 1
            
            news = st.session_state.news_collector.fetch_forex_news()
            sentiment = st.session_state.sentiment_analyzer.analyze_news(news)
            sent_score = sentiment['avg_sentiment_score']
            
            prob_up = 50 + (technical_score * 15) + (sent_score * 25)
            prob_up = max(5, min(95, prob_up))
            prob_down = 100 - prob_up
            
            # Signal display
            st.markdown("### 📈 Signal")
            
            if prob_up >= 65:
                sig = "🟢 STRONG BUY"
                sig_bg = "#28a745"
            elif prob_up >= 55:
                sig = "🟢 BUY"
                sig_bg = "#6cbe45"
            elif prob_down >= 65:
                sig = "🔴 STRONG SELL"
                sig_bg = "#dc3545"
            elif prob_down >= 55:
                sig = "🔴 SELL"
                sig_bg = "#e4605a"
            else:
                sig = "🟡 HOLD"
                sig_bg = "#ffc107"
            
            st.markdown(f"""
            <div class="signal-box" style="text-align:center;">
                <h2 style="color:{sig_bg}; margin:0;">{sig}</h2>
                <p style="font-size:2rem; margin:10px 0;">{prob_up:.0f}% / {prob_down:.0f}%</p>
                <p style="color:#888;">UP / DOWN</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📊 Details"):
                st.write(f"**Technical Score:** {technical_score:+d}")
                st.write(f"**RSI:** {rsi:.1f}")
                st.write(f"**MACD:** {macd:+.4f}")
                st.write(f"**Sentiment:** {sent_score:+.2f}")
            
            # Buy/Sell buttons
            b1, b2 = st.columns(2)
            with b1:
                st.markdown("### 🟢 BUY")
                st.button(f"Buy @ ₹{price_val:.4f}", type="primary", use_container_width=True,
                         disabled=not current_price.get('success'), 
                         on_click=lambda: execute_trade("BUY", price_val, size))
            with b2:
                st.markdown("### 🔴 SELL")
                st.button(f"Sell @ ₹{price_val:.4f}", type="secondary", use_container_width=True,
                         disabled=not current_price.get('success'),
                         on_click=lambda: execute_trade("SELL", price_val, size))
    
    # ========== RIGHT: News & Sentiment ==========
    with right:
        st.subheader("📰 News Sentiment")
        
        news = st.session_state.news_collector.fetch_forex_news()
        sentiment = st.session_state.sentiment_analyzer.analyze_news(news)
        score = sentiment['avg_sentiment_score']
        
        pct = min(100, max(0, 50 + (score * 50)))
        
        if score > 0.1:
            label = "🟢 BULLISH"
            lbl_color = "#28a745"
        elif score < -0.1:
            label = "🔴 BEARISH"
            lbl_color = "#dc3545"
        else:
            label = "🟡 NEUTRAL"
            lbl_color = "#ffc107"
        
        st.markdown(f"""
        <div style="background:#1e1e1e; padding:15px; border-radius:10px; text-align:center;">
            <h3 style="color:{lbl_color}; margin:0;">{label}</h3>
            <p style="font-size:1.5rem; margin:5px 0;">{pct:.0f}% Positive</p>
            <div style="background:#333; height:15px; border-radius:8px; overflow:hidden;">
                <div style="background:linear-gradient(to right, #dc3545, #ffc107, #28a745); width:100%; height:100%;"></div>
                <div style="position:relative; top:-18px; left:{pct}%; width:4px; height:15px; background:white;"></div>
            </div>
            <p style="color:#888; font-size:0.9rem;">
                📈 {sentiment['bullish_count']} bullish | 📉 {sentiment['bearish_count']} bearish | ⚪ {sentiment['neutral_count']} neutral
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        for item in news[:5]:
            text = f"{item.get('title', '')} {item.get('description', '')}"
            item_sent = st.session_state.sentiment_analyzer.analyze_text(text)
            
            conf = item_sent['confidence']
            s_val = item_sent['score']
            
            if item_sent['label'] == 'positive':
                badge = f"🟢 +{50 + (s_val * 50):.0f}%"
            elif item_sent['label'] == 'negative':
                badge = f"🔴 -{50 - (abs(s_val) * 50):.0f}%"
            else:
                badge = f"⚪ 50%"
            
            st.markdown(f"""
            <div class="news-card">
                <p style="margin:0; font-size:0.9rem;"><b>{item['title']}</b></p>
                <p style="margin:5px 0 0 0; color:#888; font-size:0.8rem;">_{item['source']}_</p>
                <p style="margin:5px 0 0 0; font-size:0.9rem;">{badge}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Trade History
    st.subheader("📋 Trade History")
    trades = st.session_state.simulator.get_trade_history(limit=20)
    
    if trades:
        df_t = pd.DataFrame(trades)
        df_t['pnl_f'] = df_t['pnl'].apply(lambda x: f"₹{x:.2f}" if x else "-")
        df_t['pnl_pct'] = df_t['pnl_percentage'].apply(lambda x: f"{x:.2f}%" if x else "-")
        
        display = df_t[['pair', 'direction', 'entry_price', 'exit_price', 'pnl_f', 'pnl_pct', 'status']].head(10)
        st.dataframe(display, use_container_width=True)
    else:
        st.info("No trades yet. Place your first trade!")
    
    # Footer
    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🛑 Emergency Stop", use_container_width=True):
            st.session_state.risk_manager.emergency_stop()
            st.rerun()
    with c2:
        if metrics['is_halted']:
            if st.button("▶️ Resume", use_container_width=True):
                st.session_state.risk_manager.resume_trading()
                st.rerun()
    with c3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


def execute_trade(direction, price, size):
    if price > 0:
        result = st.session_state.simulator.open_position(
            pair=st.session_state.get('pair', 'USD/INR'),
            direction=direction,
            position_size=size,
            entry_price=price
        )
        if result.get('success'):
            st.success(f"{direction} order placed @ ₹{price:.4f}")
            st.rerun()


if __name__ == "__main__":
    main()
