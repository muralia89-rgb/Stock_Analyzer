"""
Data fetching module for stock data using yfinance
"""
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

class StockDataFetcher:
    """Fetches stock data from Yahoo Finance with rate limit handling"""
    
    def __init__(self, symbol, exchange='NSE', max_retries=5):
        """
        Initialize stock data fetcher with retry logic
        
        Args:
            symbol (str): Stock ticker symbol
            exchange (str): Exchange (NSE, BSE, US)
            max_retries (int): Maximum number of retry attempts
        """
        self.symbol = symbol.upper()
        self.exchange = exchange
        self.ticker_symbol = self._get_ticker_symbol()
        self.max_retries = max_retries
        
        # Initialize with retry logic
        self.ticker = None
        self.stock_info = None
        
        for attempt in range(self.max_retries):
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}: Fetching {self.ticker_symbol}...")
                
                # Create ticker with custom session
                import requests
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                })
                
                self.ticker = yf.Ticker(self.ticker_symbol, session=session)
                
                # Try to get basic info with timeout
                # Use fast_info instead of info to avoid rate limits
                try:
                    self.stock_info = self.ticker.fast_info
                    print(f"✓ Successfully fetched data for {self.ticker_symbol}")
                    break
                except:
                    # Fallback to basic history check
                    test_data = self.ticker.history(period='5d')
                    if len(test_data) > 0:
                        print(f"✓ Successfully fetched data for {self.ticker_symbol}")
                        break
                    else:
                        raise ValueError("No data available")
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Attempt {attempt + 1} failed: {error_msg}")
                
                if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                    # Exponential backoff for rate limiting
                    wait_time = (2 ** attempt) + 1  # 2, 3, 5, 9, 17 seconds
                    print(f"⏳ Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                elif attempt < self.max_retries - 1:
                    # Regular retry with shorter wait
                    time.sleep(2)
                else:
                    raise ValueError(f"Error fetching stock {symbol} on {exchange}: {str(e)}")
        
        if not self.ticker:
            raise ValueError(f"Failed to fetch {symbol} after {self.max_retries} attempts")
    
    def _get_ticker_symbol(self):
        """Get Yahoo Finance ticker symbol based on exchange"""
        symbol = self.symbol.upper()
        
        if self.exchange == 'NSE':
            return f"{symbol}.NS"
        elif self.exchange == 'BSE':
            return f"{symbol}.BO"
        else:  # US or other
            return symbol
    
    def is_valid(self):
        """Check if stock ticker is valid"""
        try:
            # Just check if ticker exists
            return self.ticker is not None
        except:
            return False
    
    def get_current_price(self):
        """Get current stock price"""
        try:
            # Try fast_info first (no rate limit)
            if self.stock_info and hasattr(self.stock_info, 'last_price'):
                return self.stock_info.last_price
            
            # Fallback to recent history
            hist = self.ticker.history(period='1d')
            if not hist.empty:
                return hist['Close'].iloc[-1]
            
            return None
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
    
    def get_historical_data(self, period='1y'):
        """
        Get historical OHLCV data
        
        Args:
            period (str): Data period ('1mo', '3mo', '6mo', '1y', '2y', 'max')
        
        Returns:
            pd.DataFrame: Historical data with OHLCV columns
        """
        try:
            # Add retry logic for historical data
            for attempt in range(3):
                try:
                    data = self.ticker.history(period=period)
                    
                    if data.empty:
                        raise ValueError("No historical data available")
                    
                    return data
                    
                except Exception as e:
                    if "Rate limited" in str(e) and attempt < 2:
                        wait_time = (2 ** attempt) + 1
                        print(f"Rate limited getting history. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            raise
    
    def get_fundamentals(self):
        """Get fundamental data (may be limited due to rate limiting)"""
        try:
            fundamentals = {}
            
            # Try to get basic info without triggering rate limit
            try:
                if hasattr(self.ticker, 'info'):
                    info = self.ticker.info
                    
                    fundamentals['pe_ratio'] = info.get('trailingPE')
                    fundamentals['forward_pe'] = info.get('forwardPE')
                    fundamentals['peg_ratio'] = info.get('pegRatio')
                    fundamentals['price_to_book'] = info.get('priceToBook')
                    fundamentals['debt_to_equity'] = info.get('debtToEquity')
                    fundamentals['roe'] = info.get('returnOnEquity')
                    fundamentals['profit_margin'] = info.get('profitMargins')
                    fundamentals['revenue_growth'] = info.get('revenueGrowth')
                    fundamentals['earnings_growth'] = info.get('earningsGrowth')
                    fundamentals['market_cap'] = info.get('marketCap')
                    fundamentals['dividend_yield'] = info.get('dividendYield')
                    fundamentals['sector'] = info.get('sector')
                    fundamentals['industry'] = info.get('industry')
            except:
                print("⚠️ Could not fetch fundamental data (rate limited)")
                pass
            
            return fundamentals
            
        except Exception as e:
            print(f"Error fetching fundamentals: {e}")
            return {}
    
    def get_company_info(self):
        """Get company information"""
        try:
            info = {}
            
            try:
                if hasattr(self.ticker, 'info'):
                    ticker_info = self.ticker.info
                    info['name'] = ticker_info.get('longName', self.symbol)
                    info['sector'] = ticker_info.get('sector', 'Unknown')
                    info['industry'] = ticker_info.get('industry', 'Unknown')
                    info['website'] = ticker_info.get('website', '')
                    info['description'] = ticker_info.get('longBusinessSummary', '')
            except:
                # Fallback to basic info
                info['name'] = self.symbol
                info['sector'] = 'Unknown'
                info['industry'] = 'Unknown'
            
            return info
            
        except Exception as e:
            print(f"Error fetching company info: {e}")
            return {'name': self.symbol, 'sector': 'Unknown', 'industry': 'Unknown'}
