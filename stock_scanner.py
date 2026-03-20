"""
Smart Stock Scanner for Indian Market
Scans multiple stocks and recommends BUY/SELL based on comprehensive analysis
"""
import pandas as pd
from datetime import datetime
from main import StockAnalyzer
from news_fetcher import NewsFetcher
from ml_database import MLDatabase
import time

class StockScanner:
    """Scans multiple stocks and provides recommendations"""
    
    def __init__(self, holding_term='week', exchange='NSE'):
        """
        Initialize scanner
        
        Args:
            holding_term (str): 'week', 'month', or 'long_term'
            exchange (str): 'NSE', 'BSE', or 'US'
        """
        self.holding_term = holding_term
        self.exchange = exchange
        self.news_fetcher = NewsFetcher()
        self.ml_db = MLDatabase()
        self.results = []
    
    def get_stock_list(self, custom_list=None):
        """Get list of stocks to scan"""
        if custom_list:
            return custom_list
        
        # Default NSE stocks to scan (top liquid stocks)
        nse_stocks = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'ITC',
            'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TATAMOTORS',
            'SUNPHARMA', 'WIPRO', 'ONGC', 'NTPC', 'POWERGRID',
            'ULTRACEMCO', 'BAJFINANCE', 'M&M', 'TECHM', 'TITAN',
            'ADANIPORTS', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'NESTLEIND',
            'BRITANNIA', 'HEROMOTOCO', 'EICHERMOT', 'JSWSTEEL', 'TATASTEEL',
            'HINDALCO', 'COALINDIA', 'GRASIM', 'BAJAJFINSV', 'HCLTECH',
            'INDUSINDBK', 'ADANIENT', 'TATACONSUM', 'APOLLOHOSP', 'DLF'
        ]
        
        return nse_stocks
    
    def scan_stock(self, symbol):
        """Scan a single stock and return recommendation"""
        print(f"\n{'='*60}")
        print(f"Scanning: {symbol}")
        print(f"{'='*60}")
        
        try:
            # Run full analysis
            analyzer = StockAnalyzer(symbol, self.holding_term, self.exchange)
            results = analyzer.analyze()
            
            if not results:
                print(f"✗ Could not analyze {symbol}")
                return None
            
            # Safely extract data with defaults
            decision = results.get('decision') or {}
            company_info = results.get('company_info') or {}
            ml_prediction_data = results.get('ml_prediction') or {}
            
            # Get ML accuracy for this stock (if available)
            ml_accuracy = None
            if ml_prediction_data and ml_prediction_data.get('model_stats'):
                ml_stats = ml_prediction_data['model_stats']
                accuracies = []
                for stats in ml_stats.values():
                    if stats and stats.get('accuracy'):
                        try:
                            acc_str = stats['accuracy'].rstrip('%')
                            accuracies.append(float(acc_str))
                        except:
                            pass
                ml_accuracy = sum(accuracies) / len(accuracies) if accuracies else None
            
            # Get sector news sentiment
            sector = company_info.get('sector', 'Unknown')
            try:
                sector_news = self.news_fetcher.get_sectoral_news(sector)
            except:
                sector_news = {'sentiment': 'neutral', 'headlines': [], 'positive': 0, 'negative': 0}
            
            # Get stock-specific news
            company_name = company_info.get('name', '')
            try:
                # Use smart priority news system with holding term
                stock_news = self.news_fetcher.get_stock_specific_news(
                    symbol, 
                    company_name, 
                    holding_term=self.holding_term
                )
            except:
                stock_news = []

            # Get sectoral news with holding term
            sector = company_info.get('sector', 'Unknown')
            try:
                sector_news = self.news_fetcher.get_sectoral_news(
                    sector, 
                    holding_term=self.holding_term
                )
            except:
                sector_news = {'sentiment': 'neutral', 'headlines': [], 'positive': 0, 'negative': 0}
            # Get ensemble prediction
            ensemble = ml_prediction_data.get('ensemble') or {}
            
            # Calculate overall score with safe defaults
            rule_score = decision.get('confidence', 50) or 50
            ml_score = ensemble.get('confidence', 50) or 50
            
            # Adjust score based on news sentiment
            news_adjustment = 0
            if sector_news.get('sentiment') == 'bullish':
                news_adjustment = 5
            elif sector_news.get('sentiment') == 'bearish':
                news_adjustment = -5
            
            final_score = (rule_score * 0.6 + ml_score * 0.4 + news_adjustment)
            
            # Agreement between methods
            rule_signal = decision.get('decision', 'HOLD') or 'HOLD'
            ml_signal = ensemble.get('recommendation', 'HOLD') or 'HOLD'
            agreement = (rule_signal == ml_signal)
            
            # Safely get scores
            scores = decision.get('scores') or {}
            
            recommendation = {
                'symbol': symbol,
                'company_name': results.get('company_name', symbol) or symbol,
                'sector': sector,
                'current_price': results.get('current_price', 0) or 0,
                'rule_based_signal': rule_signal,
                'rule_based_confidence': rule_score,
                'ml_signal': ml_signal,
                'ml_confidence': ml_score,
                'ml_accuracy': ml_accuracy,
                'agreement': agreement,
                'final_score': final_score,
                'sector_sentiment': sector_news.get('sentiment', 'neutral'),
                'stock_news_count': len(stock_news) if stock_news else 0,
                'technical_score': scores.get('technical_score', 0) or 0,
                'fundamental_score': scores.get('fundamental_score', 0) or 0,
                'overall_score': scores.get('overall_score', 0) or 0,
                'scan_time': datetime.now()
            }
            
            print(f"✓ {symbol}: {rule_signal} (Score: {final_score:.1f})")
            
            return recommendation
        
        except Exception as e:
            print(f"✗ Error scanning {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def scan_multiple(self, stock_list=None, max_stocks=20):
        """Scan multiple stocks"""
        stocks = self.get_stock_list(stock_list)[:max_stocks]
        
        print(f"\n{'='*60}")
        print(f"  STOCK SCANNER - {self.holding_term.upper()}")
        print(f"  Scanning {len(stocks)} stocks...")
        print(f"{'='*60}")
        
        # Get market sentiment first
        try:
            market_sentiment = self.news_fetcher.get_market_sentiment()
            print(f"\n📰 Market Sentiment: {market_sentiment['sentiment'].upper()}")
            print(f"   Score: {market_sentiment.get('score', 0):.2f}")
            print(f"   Positive news: {market_sentiment.get('positive_count', 0)}")
            print(f"   Negative news: {market_sentiment.get('negative_count', 0)}")
        except Exception as e:
            print(f"✗ Could not fetch market sentiment: {e}")
            market_sentiment = {
                'sentiment': 'neutral',
                'score': 0,
                'headlines': [],
                'positive_count': 0,
                'negative_count': 0
            }
        
        results = []
        
        for idx, symbol in enumerate(stocks, 1):
            print(f"\n[{idx}/{len(stocks)}] Processing {symbol}...")
            
            result = self.scan_stock(symbol)
            if result:
                results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(2)
        
        self.results = results
        return self.create_report(market_sentiment)
    
    def create_report(self, market_sentiment=None):
        """Create scan report with recommendations"""
        if not self.results:
            return None
        
        df = pd.DataFrame(self.results)
        
        # Sort by final score
        df = df.sort_values('final_score', ascending=False)
        
        # Categorize
        buy_recommendations = df[
            (df['rule_based_signal'] == 'BUY') | 
            (df['ml_signal'] == 'BUY')
        ].head(10)
        
        sell_recommendations = df[
            (df['rule_based_signal'] == 'SELL') | 
            (df['ml_signal'] == 'SELL')
        ].head(10)
        
        # High confidence BUYs (both methods agree)
        strong_buys = df[
            (df['rule_based_signal'] == 'BUY') & 
            (df['ml_signal'] == 'BUY') &
            (df['final_score'] > 70)
        ]
        
        # High confidence SELLs (both methods agree)
        strong_sells = df[
            (df['rule_based_signal'] == 'SELL') & 
            (df['ml_signal'] == 'SELL') &
            (df['final_score'] < 40)
        ]
        
        # Use provided market sentiment or default
        if market_sentiment is None:
            market_sentiment = {
                'sentiment': 'neutral',
                'score': 0,
                'headlines': [],
                'positive_count': 0,
                'negative_count': 0
            }
        
        report = {
            'scan_summary': {
                'total_scanned': len(self.results),
                'buy_signals': len(df[df['rule_based_signal'] == 'BUY']),
                'sell_signals': len(df[df['rule_based_signal'] == 'SELL']),
                'hold_signals': len(df[df['rule_based_signal'] == 'HOLD']),
                'scan_time': datetime.now(),
                'holding_term': self.holding_term
            },
            'all_results': df,
            'buy_recommendations': buy_recommendations,
            'sell_recommendations': sell_recommendations,
            'strong_buys': strong_buys,
            'strong_sells': strong_sells,
            'top_opportunities': df.head(10),  # Top 10 by score
            'market_sentiment': market_sentiment
        }
        
        return report
    
    def print_report(self, report):
        """Print formatted scan report"""
        print(f"\n{'='*80}")
        print(f"  SCAN REPORT - {report['scan_summary']['holding_term'].upper()}")
        print(f"  {report['scan_summary']['scan_time']}")
        print(f"{'='*80}")
        
        print(f"\n📊 Summary:")
        print(f"   Total stocks scanned: {report['scan_summary']['total_scanned']}")
        print(f"   🟢 BUY signals: {report['scan_summary']['buy_signals']}")
        print(f"   🔴 SELL signals: {report['scan_summary']['sell_signals']}")
        print(f"   🟡 HOLD signals: {report['scan_summary']['hold_signals']}")
        
        print(f"\n{'='*80}")
        print(f"  🌟 STRONG BUY RECOMMENDATIONS (Both Methods Agree)")
        print(f"{'='*80}")
        
        if len(report['strong_buys']) > 0:
            for idx, row in report['strong_buys'].iterrows():
                print(f"\n🟢 {row['symbol']} - {row['company_name']}")
                print(f"   Price: ₹{row['current_price']:.2f}")
                print(f"   Sector: {row['sector']}")
                print(f"   Score: {row['final_score']:.1f}")
                print(f"   Rule-Based: {row['rule_based_signal']} ({row['rule_based_confidence']:.1f}%)")
                print(f"   ML Prediction: {row['ml_signal']} ({row['ml_confidence']:.1f}%)")
                print(f"   Sector Sentiment: {row['sector_sentiment']}")
        else:
            print("   No strong buy signals found.")
        
        print(f"\n{'='*80}")
        print(f"  ⚠️ SELL RECOMMENDATIONS")
        print(f"{'='*80}")
        
        if len(report['sell_recommendations']) > 0:
            for idx, row in report['sell_recommendations'].head(5).iterrows():
                print(f"\n🔴 {row['symbol']} - {row['company_name']}")
                print(f"   Price: ₹{row['current_price']:.2f}")
                print(f"   Score: {row['final_score']:.1f}")
                print(f"   Signal: {row['rule_based_signal']}")
        else:
            print("   No sell signals found.")
        
        print(f"\n{'='*80}\n")
