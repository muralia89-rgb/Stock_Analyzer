"""
Streamlit web application for stock analysis with ML continuous learning and Stock Scanner
Run with: streamlit run app.py
"""
import streamlit as st
from main import StockAnalyzer
from utils import format_currency, format_percentage, get_signal_emoji
from stock_symbols import search_stocks, get_stocks_by_exchange, format_stock_display
from chart_plotter import InteractiveChartPlotter
from stock_scanner import StockScanner
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Stock Analysis System with AI",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = None
if 'current_holding_term' not in st.session_state:
    st.session_state.current_holding_term = None
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# Title
st.title("📊 AI-Powered Stock Analysis System")
st.markdown("*With Machine Learning, News Analysis & Smart Stock Scanner*")
st.markdown("---")

# Create main tabs
main_tab1, main_tab2 = st.tabs(["🔍 Single Stock Analysis", "🎯 Smart Stock Scanner"])

# ==================== TAB 1: SINGLE STOCK ANALYSIS ====================

with main_tab1:
    # Sidebar for inputs
    st.sidebar.header("Input Parameters")
    
    # Exchange selection
    exchange = st.sidebar.selectbox(
        "Exchange",
        ["NSE (India)", "BSE (India)", "US Market"],
        index=0,
        help="Select the stock exchange"
    )
    
    exchange_map = {
        "NSE (India)": "NSE",
        "BSE (India)": "BSE",
        "US Market": "US"
    }
    exchange_code = exchange_map[exchange]
    
    st.sidebar.subheader("Stock Selection")
    
    all_stocks = get_stocks_by_exchange(exchange_code)
    stock_options = [format_stock_display(sym, name) for sym, name in all_stocks.items()]
    
    selected_stock = st.sidebar.selectbox(
        "Search and select stock",
        options=["Select a stock..."] + sorted(stock_options),
        index=0,
        help="Start typing to search by symbol or company name"
    )
    
    if selected_stock and selected_stock != "Select a stock...":
        symbol = selected_stock.split(" - ")[0]
    else:
        symbol = None
    
    with st.sidebar.expander("Or enter symbol manually"):
        manual_symbol = st.text_input(
            "Type stock symbol",
            value="",
            help="Enter stock ticker directly"
        ).upper()
        
        if manual_symbol:
            symbol = manual_symbol
    
    holding_term_display = st.sidebar.selectbox(
        "Holding Term",
        ["Week (Short-term)", "Month (Medium-term)", "Long-term Investment"]
    )
    
    term_map = {
        "Week (Short-term)": "week",
        "Month (Medium-term)": "month",
        "Long-term Investment": "long_term"
    }
    holding_term = term_map[holding_term_display]
    
    if symbol:
        company_name = all_stocks.get(symbol, "Unknown Company")
        st.sidebar.success(f"**Selected:** {symbol}\n\n{company_name}")
    
    analyze_button = st.sidebar.button("🔍 Analyze Stock", type="primary", disabled=not symbol)
    
    if st.session_state.analysis_results is not None:
        if st.sidebar.button("🔄 Clear Results"):
            st.session_state.analysis_results = None
            st.session_state.analyzer = None
            st.session_state.current_symbol = None
            st.session_state.current_holding_term = None
            st.rerun()
    
    # Run analysis if button clicked OR if toggling indicators
    if analyze_button or (st.session_state.analysis_results is not None and 
                          symbol == st.session_state.current_symbol and 
                          holding_term == st.session_state.current_holding_term):
        
        if analyze_button or st.session_state.analysis_results is None:
            if not symbol:
                st.error("⚠️ Please select a stock symbol")
            else:
                try: 
                    with st.spinner(f"Analyzing {symbol}... This may take 1-2 minutes for ML training..."):
                        st.write(f"DEBUG: Starting analysis for {symbol}")
                        analyzer = StockAnalyzer(symbol, holding_term, exchange_code)
                        st.write("DEBUG: Fetching data...")
                        results = analyzer.analyze()

                        st.write("DEBUG: Analysis complete!")

                        if results:                      
                            st.session_state.analysis_results = results
                            st.session_state.analyzer = analyzer
                            st.session_state.current_symbol = symbol
                            st.session_state.current_holding_term = holding_term
                        else:
                            st.error("❌ Analysis returned no results")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.error(f"Error type: {type(e).__name__}")
        
                    # Show full traceback for debugging
                    import traceback
                    st.code(traceback.format_exc())
        
        results = st.session_state.analysis_results
        analyzer = st.session_state.analyzer
        
        if results:
            # Company info section
            st.header(f"{results.get('company_name', symbol)}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Symbol", results['symbol'])
            
            with col2:
                current_price = results.get('current_price')
                if current_price:
                    st.metric("Current Price", f"{current_price:.2f}")
            
            with col3:
                company_info = results.get('company_info', {})
                sector = company_info.get('sector', 'N/A')
                st.metric("Sector", sector)
            
            with col4:
                st.metric("Holding Term", holding_term.replace('_', ' ').title())
            
            st.markdown("---")
            
            # Interactive Chart Section
            st.subheader("📊 Interactive Price Chart")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                timeframe = st.selectbox(
                    "Select Timeframe",
                    ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "All Data"],
                    index=3,
                    key="timeframe_selector"
                )
            
            with col2:
                chart_view = st.radio(
                    "View",
                    ["Full Chart", "Price Only"],
                    horizontal=True,
                    key="chart_view_selector"
                )
            
            st.write("**Select Indicators to Display:**")
            indicator_cols = st.columns(6)
            
            with indicator_cols[0]:
                show_sma = st.checkbox("SMA", value=True, key="show_sma")
            with indicator_cols[1]:
                show_ema = st.checkbox("EMA", value=False, key="show_ema")
            with indicator_cols[2]:
                show_bb = st.checkbox("Bollinger Bands", value=False, key="show_bb")
            with indicator_cols[3]:
                show_rsi = st.checkbox("RSI", value=True, key="show_rsi")
            with indicator_cols[4]:
                show_macd = st.checkbox("MACD", value=True, key="show_macd")
            with indicator_cols[5]:
                show_volume = st.checkbox("Volume", value=True, key="show_volume")
            
            indicators = []
            if show_sma:
                indicators.append('sma')
            if show_ema:
                indicators.append('ema')
            if show_bb:
                indicators.append('bollinger')
            if show_rsi:
                indicators.append('rsi')
            if show_macd:
                indicators.append('macd')
            if show_volume:
                indicators.append('volume')
            
            try:
                timeframe_map = {
                    "1 Month": "1mo",
                    "3 Months": "3mo",
                    "6 Months": "6mo",
                    "1 Year": "1y",
                    "2 Years": "2y",
                    "All Data": "max"
                }
                
                chart_data = analyzer.fetcher.get_historical_data(
                    period=timeframe_map[timeframe]
                )
                
                plotter = InteractiveChartPlotter(chart_data, symbol)
                
                if chart_view == "Full Chart":
                    fig = plotter.create_candlestick_chart(show_indicators=indicators)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = go.Figure(data=[
                        go.Candlestick(
                            x=chart_data.index,
                            open=chart_data['Open'],
                            high=chart_data['High'],
                            low=chart_data['Low'],
                            close=chart_data['Close'],
                            increasing_line_color='#26a69a',
                            decreasing_line_color='#ef5350'
                        )
                    ])
                    
                    fig.update_layout(
                        title=f'{symbol} - Price Chart',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        height=600,
                        template='plotly_white',
                        hovermode='x unified'
                    )
                    
                    fig.update_xaxes(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(step="all", label="All")
                            ])
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Could not load chart: {str(e)}")
            
            st.markdown("---")
            
            # Decision section
            decision = results['decision']
            decision_text = decision['decision']
            confidence = decision['confidence']
            
            if decision_text == 'BUY':
                color = 'green'
            elif decision_text == 'SELL':
                color = 'red'
            else:
                color = 'orange'
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Rule-Based Recommendation")
                st.markdown(f"### :{color}[{decision_text}]")
                st.progress(confidence / 100)
                st.write(f"**Confidence:** {confidence:.1f}%")
                
                if decision['meets_threshold']:
                    st.success(f"✅ Meets minimum confidence threshold ({decision['min_confidence']}%)")
                else:
                    st.warning(f"⚠️ Below minimum confidence threshold ({decision['min_confidence']}%)")
            
            with col2:
                st.subheader("📊 Signal Distribution")
                signal_counts = decision['signal_counts']
                
                signal_df = pd.DataFrame({
                    'Signal': ['Buy', 'Sell', 'Hold'],
                    'Count': [
                        signal_counts['buy'],
                        signal_counts['sell'],
                        signal_counts['hold']
                    ]
                })
                
                st.bar_chart(signal_df.set_index('Signal'))
            
            st.subheader("💡 Analysis Reasoning")
            for reason in decision['reasoning']:
                st.write(f"• {reason}")
            
            st.markdown("---")
            st.warning("""
            **⚠️ DISCLAIMER:**
            This analysis is for informational purposes only and should NOT be considered financial advice.
            """)
    
    else:
        st.info("""
        👈 **Select a stock** from the dropdown in the sidebar and click **Analyze Stock** to begin.
        
        This system analyzes stocks using:
        - 📊 **Technical Indicators:** RSI, MACD, Moving Averages, Bollinger Bands, Volume
        - 💰 **Fundamental Metrics:** P/E Ratio, PEG Ratio, ROE, Debt/Equity, Growth Rates
        - ⚙️ **Rule-Based Engine:** Customized rules for different holding periods
        - 📈 **Interactive Charts:** Zoom, pan, and explore price action
        - 🤖 **AI/ML Predictions:** Self-learning models that improve over time
        """)

# ==================== TAB 2: SMART STOCK SCANNER ====================

with main_tab2:
    st.header("🎯 Smart Stock Scanner")
    st.write("*Scan multiple stocks and get AI-powered BUY/SELL recommendations*")
    
    st.markdown("---")
    
    # Scanner settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scan_holding_term = st.selectbox(
            "Holding Term for Scan",
            ["Week (Short-term)", "Month (Medium-term)", "Long-term Investment"],
            key="scan_holding_term"
        )
        scan_term = term_map[scan_holding_term]
    
    with col2:
        scan_exchange = st.selectbox(
            "Exchange to Scan",
            ["NSE (India)", "BSE (India)", "US Market"],
            index=0,
            key="scan_exchange"
        )
        scan_exchange_code = exchange_map[scan_exchange]
    
    with col3:
        max_stocks = st.number_input(
            "Number of stocks to scan",
            min_value=1,
            max_value=50,
            value=1,
            step=5,
            help="More stocks = longer scan time"
        )
    
    # Custom stock list option
    use_custom_list = st.checkbox("Use custom stock list (advanced)")
    
    if use_custom_list:
        custom_stocks_input = st.text_area(
            "Enter stock symbols (one per line or comma-separated)",
            value="",
            height=100
        )
        custom_stocks = [s.strip().upper() for s in custom_stocks_input.replace(',', '\n').split('\n') if s.strip()]
    else:
        custom_stocks = None
    
    # Scan button
    scan_button = st.button("🚀 Start Scan", type="primary")
    
    if scan_button:
        with st.spinner(f"Scanning stocks... This will take several minutes..."):
            try:
                scanner = StockScanner(holding_term=scan_term, exchange=scan_exchange_code)
                report = scanner.scan_multiple(stock_list=custom_stocks, max_stocks=max_stocks)
                
                st.session_state.scan_results = report
                st.success("✅ Scan completed!")
                
            except Exception as e:
                st.error(f"❌ Error during scan: {str(e)}")
                st.session_state.scan_results = None
    
    # Display scan results
    if st.session_state.scan_results:
        report = st.session_state.scan_results
        
        st.markdown("---")
        
        # Add holding term filter
        st.subheader("🔍 Filter Results")
        display_holding_term = st.selectbox(
            "View recommendations for:",
            ["Current Scan Term", "Week (Short-term)", "Month (Medium-term)", "Long-term Investment"],
            key="display_holding_term"
        )
        
        if display_holding_term == "Current Scan Term":
            st.info(f"Showing results for: **{scan_term.replace('_', ' ').title()}**")
        else:
            st.warning(f"⚠️ Note: Scan was performed for **{scan_term.replace('_', ' ').title()}** but you're viewing it as **{display_holding_term}**. For accurate results, run a new scan with the desired holding term.")
        
        st.markdown("---")
        
        # Summary metrics
        st.subheader("📊 Scan Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Scanned", report['scan_summary']['total_scanned'])
        with col2:
            st.metric("🟢 BUY Signals", report['scan_summary']['buy_signals'])
        with col3:
            st.metric("🔴 SELL Signals", report['scan_summary']['sell_signals'])
        with col4:
            st.metric("🟡 HOLD Signals", report['scan_summary']['hold_signals'])
        with col5:
            st.metric("Holding Term", scan_term.replace('_', ' ').title())
        
        st.markdown("---")
        
        # Market sentiment
        market_sentiment = report['market_sentiment']
        
        st.subheader("📰 Indian Market Sentiment")
        
        sentiment_color = 'green' if market_sentiment['sentiment'] == 'bullish' else ('red' if market_sentiment['sentiment'] == 'bearish' else 'gray')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### :{sentiment_color}[{market_sentiment['sentiment'].upper()}]")
            st.caption("Overall market sentiment from news")
        
        with col2:
            st.metric("Positive News", market_sentiment['positive_count'])
        
        with col3:
            st.metric("Negative News", market_sentiment['negative_count'])
        
        with st.expander("📰 Latest Market Headlines"):
            for headline in market_sentiment['headlines'][:10]:
                st.write(f"• **{headline['title']}**")
                st.caption(f"Source: {headline['source']} | {headline['published']}")
        
        st.markdown("---")
        st.subheader("📰 Recent News & Sentiment")
            
            if 'news' in results and results['news']['articles']:
                news_summary = results['news']['summary']
                
                # Show news summary metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Articles", news_summary.get('total_articles', 0))
                col2.metric("Stock-Specific", news_summary.get('stock_specific', 0), 
                           help="News specifically about this company")
                col3.metric("Sector-Related", news_summary.get('sector_related', 0),
                           help="News about the industry/sector")
                col4.metric("General Market", news_summary.get('general_market', 0),
                           help="Broader market news")
                
                st.write("")  # Spacing
                
                # Display articles with relevance badges
                articles = results['news']['articles'][:10]  # Show top 10
                
                for idx, article in enumerate(articles, 1):
                    relevance = article.get('relevance', 'general')
                    source = article.get('source', 'Unknown')
                    title = article.get('title', 'No title')
                    link = article.get('link', '#')
                    date = article.get('date')
                    
                    # Create relevance badge with color
                    if relevance == 'stock-specific':
                        badge_emoji = "🎯"
                        badge_text = "STOCK-SPECIFIC"
                        badge_color = "#28a745"  # Green
                    elif relevance == 'sector':
                        badge_emoji = "📊"
                        badge_text = "SECTOR-RELATED"
                        badge_color = "#ffc107"  # Yellow
                    else:
                        badge_emoji = "📈"
                        badge_text = "MARKET NEWS"
                        badge_color = "#6c757d"  # Gray
                    
                    # Display article with styled badge
                    col1, col2 = st.columns([1, 5])
                    
                    with col1:
                        st.markdown(f"**{badge_emoji}**")
                    
                    with col2:
                        st.markdown(
                            f'<span style="background-color: {badge_color}; color: white; padding: 2px 6px; '
                            f'border-radius: 3px; font-size: 10px; font-weight: bold;">{badge_text}</span> '
                            f'<span style="color: #666; font-size: 12px;">| {source}</span>',
                            unsafe_allow_html=True
                        )
                        st.markdown(f"**[{title}]({link})**")
                        
                        if date:
                            try:
                                date_str = date.strftime('%B %d, %Y at %I:%M %p')
                                st.caption(f"📅 {date_str}")
                            except:
                                pass
                    
                    if idx < len(articles):  # Add divider except after last item
                        st.write("")
            
            else:
                st.info("📰 No recent news found for this stock. This could mean:")
                st.write("- The stock is less covered by financial media")
                st.write("- No significant news in the selected timeframe")
                st.write("- News sources are temporarily unavailable")

        # Strong Buy Recommendations
        st.subheader("🌟 STRONG BUY Recommendations")
        st.write("*Both Rule-Based and ML models agree + High confidence (Score ≥ 70)*")

        if len(report['strong_buys']) > 0:
            strong_buy_display = report['strong_buys'][['symbol', 'company_name', 'current_price', 
                                                         'final_score', 'rule_based_confidence', 
                                                         'ml_confidence', 'sector_sentiment']].copy()
            strong_buy_display.columns = ['Symbol', 'Company', 'Price (₹)', 'Score', 
                                          'Rule Confidence', 'ML Confidence', 'Sector']
            
            # Color function for strong buys
            def color_strong_buys(row):
                score = row['Score']
                if score >= 80:
                    color = '#66BB6A'  # Darker green for very strong
                else:
                    color = '#90EE90'  # Light green for strong
                return [f'background-color: {color}'] * len(row)
            
            styled_strong_buys = strong_buy_display.style.apply(color_strong_buys, axis=1)
            
            st.dataframe(
                styled_strong_buys,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No strong buy signals found in current scan.")
        
        st.markdown("---")

        # Top Opportunities
        st.subheader("🔝 Top 10 Opportunities")
        st.write("*Ranked by overall score*")

        # Add Score Legend
        with st.expander("📊 Understanding the Score", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Score Calculation:**
                - 60% Rule-based confidence
                - 40% ML confidence
                - ±5% News sentiment adjustment
                
                **Range:** 0 to 100
                """)
            
            with col2:
                st.markdown("""
                **Color Guide:**
                - 🟢 **70-100**: Strong BUY
                - 🟡 **60-70**: Moderate BUY
                - 🟠 **50-60**: HOLD/Uncertain
                - 🔴 **40-50**: Weak SELL
                - 🔴 **0-40**: Strong SELL
                """)

        top_10 = report['top_opportunities'][['symbol', 'company_name', 'sector', 'current_price',
                                               'rule_based_signal', 'ml_signal', 'final_score',
                                               'agreement']].copy()
        top_10.columns = ['Symbol', 'Company', 'Sector', 'Price', 'Rule Signal', 
                         'ML Signal', 'Score', 'Agreement']

        # Function to apply colors based on absolute thresholds
        def color_score_row(row):
            """Apply color to entire row based on score"""
            score = row['Score']
            
            if score >= 70:
                color = '#90EE90'  # Light green - Strong BUY
            elif score >= 60:
                color = '#FFFF99'  # Light yellow - Moderate BUY
            elif score >= 50:
                color = '#FFE5B4'  # Peach - HOLD/Uncertain
            elif score >= 40:
                color = '#FFB6C1'  # Light pink - Weak SELL
            else:
                color = '#FF9999'  # Light red - Strong SELL
            
            return [f'background-color: {color}'] * len(row)

        # Apply styling
        styled_top_10 = top_10.style.apply(color_score_row, axis=1)

        st.dataframe(
            styled_top_10,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # All BUY recommendations
        st.subheader("🟢 All BUY Recommendations")
        
        if len(report['buy_recommendations']) > 0:
            buy_display = report['buy_recommendations'][['symbol', 'company_name', 'sector', 
                                                         'current_price', 'final_score', 
                                                         'rule_based_signal', 'ml_signal']].copy()
            buy_display.columns = ['Symbol', 'Company', 'Sector', 'Price (₹)', 
                                  'Score', 'Rule', 'ML']
            
            st.dataframe(buy_display, use_container_width=True, hide_index=True)
        else:
            st.info("No buy recommendations found.")
        
        st.markdown("---")
        
        # SELL recommendations
        st.subheader("🔴 SELL Recommendations")
        
        if len(report['sell_recommendations']) > 0:
            sell_display = report['sell_recommendations'][['symbol', 'company_name', 'sector',
                                                           'current_price', 'final_score',
                                                           'rule_based_signal', 'ml_signal']].copy()
            sell_display.columns = ['Symbol', 'Company', 'Sector', 'Price (₹)',
                                   'Score', 'Rule', 'ML']
            
            st.dataframe(sell_display, use_container_width=True, hide_index=True)
        else:
            st.info("No sell recommendations found.")
        
        st.markdown("---")
        
        # Download options
        st.subheader("💾 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Full report CSV
            csv_full = report['all_results'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Report (CSV)",
                data=csv_full,
                file_name=f"stock_scan_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download complete scan results with all columns"
            )
        
        with col2:
            # BUY recommendations only
            if len(report['buy_recommendations']) > 0:
                csv_buy = report['buy_recommendations'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="🟢 Download BUY List (CSV)",
                    data=csv_buy,
                    file_name=f"buy_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download only BUY recommendations"
                )
        
        with col3:
            # Strong BUYs only
            if len(report['strong_buys']) > 0:
                csv_strong = report['strong_buys'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="🌟 Download Strong BUYs (CSV)",
                    data=csv_strong,
                    file_name=f"strong_buys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download only strong BUY recommendations"
                )
        
        st.markdown("---")
        st.warning("""
        **⚠️ SCANNER DISCLAIMER:**
        - Scanner results are automated recommendations based on technical/fundamental analysis and AI models
        - Not financial advice - always do your own research
        - News sentiment is based on headline analysis and may not reflect full context
        - Past ML accuracy does not guarantee future results
        - Consult a financial advisor before making investment decisions
        """)
    
    else:
        st.info("""
        ### 🚀 How the Smart Scanner Works:
        
        1. **Scans Multiple Stocks** - Analyzes 5-50 NSE stocks at once
        2. **Full Analysis** - Runs complete technical + fundamental + ML analysis on each
        3. **News Integration** - Fetches latest Indian market news and sector sentiment
        4. **ML Database** - Uses historical ML accuracy to weight predictions
        5. **Smart Ranking** - Combines all factors into a final confidence score
        6. **Clear Recommendations** - Shows strong BUYs, top opportunities, and SELLs
        
        ### 📊 What You Get:
        - **Market Sentiment** - Overall Indian market mood from news
        - **Strong BUYs** - Stocks where both methods agree with high confidence
        - **Top 10 Opportunities** - Best ranked stocks by score
        - **All BUY/SELL Lists** - Complete recommendations
        - **Exportable Reports** - Download as CSV (Full/BUY only/Strong BUYs)
        - **Filter by Holding Term** - View recommendations for your preferred timeframe
        
        ### ⏱️ Scan Time:
        - 10 stocks: ~3-5 minutes
        - 20 stocks: ~6-10 minutes
        - 50 stocks: ~15-25 minutes
        
        **Click "Start Scan" to begin!**
        """)
