"""
Main application module - orchestrates the stock analysis
"""
from data_fetcher import StockDataFetcher
from technical_analyzer import TechnicalAnalyzer
from fundamental_analyzer import FundamentalAnalyzer
from rule_engine import RuleEngine
from utils import format_output, validate_inputs
import sys

class StockAnalyzer:
    """Main class that orchestrates stock analysis"""
    
    def __init__(self, symbol, holding_term, exchange='NSE'):
        """
        Initialize stock analyzer
        
        Args:
            symbol (str): Stock ticker symbol
            holding_term (str): 'week', 'month', or 'long_term'
            exchange (str): 'NSE', 'BSE', or 'US' (default: 'NSE')
        """
        # Validate inputs
        validation = validate_inputs(symbol, holding_term)
        if not validation['valid']:
            raise ValueError(validation['error'])
        
        self.symbol = symbol.upper()
        self.holding_term = holding_term
        self.exchange = exchange
        self.fetcher = None
        self.technical_signals = []
        self.fundamental_signals = []
        self.decision = None
    
    def fetch_data(self):
        """Fetch all required data"""
        print(f"\n📊 Fetching data for {self.symbol} ({self.exchange})...")
        
        try:
            self.fetcher = StockDataFetcher(self.symbol, self.exchange)
            
            # Validate stock exists
            if not self.fetcher.is_valid():
                print(f"❌ Invalid or non-existent stock symbol: {self.symbol}")
                return False
            
            # Try to get current price
            price = self.fetcher.get_current_price()
            if not price:
                print("❌ Could not fetch current price")
                return False
            
            print(f"✓ Data fetched successfully - Price: {price}")
            return True
            
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def perform_technical_analysis(self):
        """Perform technical analysis"""
        print("\n🔍 Performing technical analysis...")
        
        try:
            # Get historical data based on holding term
            if self.holding_term == 'week':
                period = '3mo'  # 3 months for short-term
            elif self.holding_term == 'month':
                period = '1y'   # 1 year for medium-term
            else:  # long_term
                period = '2y'   # 2 years for long-term
            
            historical_data = self.fetcher.get_historical_data(period=period)
            
            # Initialize technical analyzer with holding_term
            tech_analyzer = TechnicalAnalyzer(historical_data, self.holding_term)
            
            # Get all technical signals
            self.technical_signals = tech_analyzer.get_all_technical_signals()
            
            print(f"✓ Analyzed {len(self.technical_signals)} technical indicators")
            return True
            
        except Exception as e:
            print(f"✗ Error in technical analysis: {str(e)}")
            return False
    
    def perform_fundamental_analysis(self):
        """Perform fundamental analysis"""
        print("\n📈 Performing fundamental analysis...")
        
        try:
            # Get fundamental data
            fundamentals = self.fetcher.get_fundamentals()
            
            if not fundamentals:
                print("⚠ Warning: Limited fundamental data available")
                self.fundamental_signals = []
                return True
            
            # Initialize fundamental analyzer
            fund_analyzer = FundamentalAnalyzer(fundamentals)
            
            # Get all fundamental signals
            self.fundamental_signals = fund_analyzer.get_all_fundamental_signals()
            
            print(f"✓ Analyzed {len(self.fundamental_signals)} fundamental indicators")
            return True
            
        except Exception as e:
            print(f"✗ Error in fundamental analysis: {str(e)}")
            return False
        
    def fetch_news(self):
        """Fetch stock-specific news"""
        print("\n📰 Fetching news...")
        
        try:
            from news_fetcher import NewsFetcher
            
            news_fetcher = NewsFetcher()
            
            # Get company info for better news search
            company_info = self.fetcher.get_company_info()
            company_name = company_info.get('name', self.symbol)
            sector = company_info.get('sector', 'Unknown')
            
            # Determine timeframe based on holding term
            if self.holding_term == 'week':
                timeframe = 'week'
            elif self.holding_term == 'month':
                timeframe = 'month'
            else:
                timeframe = 'long'
            
            # Fetch stock-specific news
            news = news_fetcher.fetch_stock_news(
                symbol=self.symbol,
                company_name=company_name,
                sector=sector,
                timeframe=timeframe
            )
            
            # Get news summary
            summary = news_fetcher.get_news_summary(news)
            
            print(f"✓ Found {summary['total_articles']} articles:")
            print(f"  - Stock-specific: {summary['stock_specific']}")
            print(f"  - Sector-related: {summary['sector_related']}")
            print(f"  - General market: {summary['general_market']}")
            
            return {
                'articles': news,
                'summary': summary
            }
            
        except Exception as e:
            print(f"⚠️ News fetch failed: {e}")
            return {
                'articles': [],
                'summary': {'total_articles': 0, 'stock_specific': 0, 'sector_related': 0, 'general_market': 0}
            }
    
    def perform_ml_prediction(self):
        """Perform ML-based prediction with continuous learning"""
        print("\n🤖 Performing ML prediction with continuous learning...")
        
        try:
            from ml_continuous_learning import ContinuousLearningSystem
            
            # Initialize learning system
            learning_system = ContinuousLearningSystem()
            
            # Update outcomes for past predictions first
            print("Checking for due predictions to update...")
            learning_system.update_outcomes()
            
            # Get enough historical data for ML
            historical_data = self.fetcher.get_historical_data(period='2y')
            
            # Determine holding style
            if self.holding_term == 'week':
                style = 'swing'
            else:
                style = 'invest'
            
            # Check if models need retraining
            print("Checking if models need retraining...")
            learning_system.retrain_if_needed(self.symbol, historical_data, style)
            
            # Make prediction and store it
            ml_results = learning_system.make_prediction_and_store(
                self.symbol, historical_data, style
            )
            
            # Get model statistics
            model_stats = {}
            for model_name in ['lstm', 'xgboost', 'random_forest', 'prophet']:
                stats = learning_system.get_model_statistics(model_name, self.symbol)
                if stats:
                    model_stats[model_name] = stats
            
            ml_results['model_stats'] = model_stats
            ml_results['learning_system'] = learning_system
            
            print("✓ ML prediction completed with continuous learning")
            return ml_results
            
        except Exception as e:
            print(f"✗ Error in ML prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def apply_rules(self):
        """Apply rule engine to make decision"""
        print("\n⚙️ Applying decision rules...")
        
        try:
            # Initialize rule engine
            engine = RuleEngine(self.holding_term)
            
            # Make decision
            self.decision = engine.make_decision(
                self.technical_signals,
                self.fundamental_signals
            )
            
            print("✓ Decision made")
            return True
            
        except Exception as e:
            print(f"✗ Error applying rules: {str(e)}")
            return False
    
    def analyze(self):
        """
        Run complete analysis"""
        import traceback
        
        print(f"\n{'='*60}")
        print(f"  STOCK ANALYSIS: {self.symbol} ({self.exchange})")
        print(f"  Holding Term: {self.holding_term.upper()}")
        print(f"{'='*60}")
        
        # Step 1: Fetch data
        if not self.fetch_data():
            return None
        
        # Step 2: Technical analysis
        if not self.perform_technical_analysis():
            return None
        
        # Step 3: Fundamental analysis
        if not self.perform_fundamental_analysis():
            return None

        # Step 4: Fetch news (NEW!)
        news_data = self.fetch_news()
        
        # Step 5: ML Prediction with continuous learning
        ml_prediction = self.perform_ml_prediction()
        
        # Step 6: Apply rules and make decision
        if not self.apply_rules():
            return None
        
        # Compile results
        results = {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'company_name': self.fetcher.get_company_info().get('name', 'N/A'),
            'current_price': self.fetcher.get_current_price(),
            'holding_term': self.holding_term,
            'decision': self.decision,
            'technical_signals': self.technical_signals,
            'fundamental_signals': self.fundamental_signals,
            'company_info': self.fetcher.get_company_info(),
            'ml_prediction': ml_prediction,
            'news': news_data
        }
        
        return results
    
    def print_results(self, results):
        """Print formatted results"""
        if not results:
            print("\n❌ Analysis failed - no results to display")
            return
        
        format_output(results)


def main():
    """Main entry point for command-line usage"""
    print("\n" + "="*60)
    print("  STOCK ANALYSIS SYSTEM")
    print("="*60)
    
    try:
        # Get exchange selection
        print("\nSelect exchange:")
        print("  1. NSE (National Stock Exchange, India)")
        print("  2. BSE (Bombay Stock Exchange, India)")
        print("  3. US Stock Market (NYSE, NASDAQ)")
        
        exchange_choice = input("\nEnter choice (1/2/3, default: 1): ").strip() or '1'
        
        exchange_map = {
            '1': 'NSE',
            '2': 'BSE',
            '3': 'US'
        }
        
        exchange = exchange_map.get(exchange_choice, 'NSE')
        
        # Get user input based on exchange
        if exchange == 'NSE':
            print("\n💡 Popular NSE stocks: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK")
            symbol = input("\n📊 Enter NSE stock symbol (e.g., RELIANCE, TCS): ").strip()
        elif exchange == 'BSE':
            print("\n💡 Popular BSE stocks: RELIANCE, TCS, INFY, HDFCBANK")
            symbol = input("\n📊 Enter BSE stock symbol (e.g., RELIANCE, TCS): ").strip()
        else:
            print("\n💡 Popular US stocks: AAPL, MSFT, GOOGL, AMZN, TSLA")
            symbol = input("\n📊 Enter US stock symbol (e.g., AAPL, MSFT): ").strip()
        
        if not symbol:
            print("\n❌ Stock symbol is required. Please run again.")
            return
        
        print("\nSelect holding term:")
        print("  1. Week (short-term trading)")
        print("  2. Month (medium-term trading)")
        print("  3. Long-term (investment)")
        
        term_choice = input("\nEnter choice (1/2/3): ").strip()
        
        # Map choice to holding term
        term_map = {
            '1': 'week',
            '2': 'month',
            '3': 'long_term'
        }
        
        holding_term = term_map.get(term_choice)
        
        if not holding_term:
            print("\n❌ Invalid choice. Please run again and select 1, 2, or 3.")
            return
        
        # Run analysis
        analyzer = StockAnalyzer(symbol, holding_term, exchange)
        results = analyzer.analyze()
        
        # Display results
        if results:
            analyzer.print_results(results)
        else:
            print("\n❌ Analysis failed. Please check the stock symbol and try again.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTips:")
        print("  • Make sure the stock symbol is correct")
        print("  • Check your internet connection")
        print("  • Try a different stock symbol")
        sys.exit(1)


if __name__ == "__main__":
    main()
