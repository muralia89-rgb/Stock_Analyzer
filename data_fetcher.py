"""
Data fetching module - retrieves stock data from online sources
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockDataFetcher:
    """Fetches stock data from Yahoo Finance"""
    
    def __init__(self, symbol, exchange='NSE'):
        """
        Initialize with stock symbol
        
        Args:
            symbol (str): Stock ticker symbol (e.g., 'RELIANCE', 'TCS')
            exchange (str): Exchange - 'NSE', 'BSE', or 'US' (default: 'NSE')
        """
        self.original_symbol = symbol.upper()
        self.exchange = exchange.upper()
        
        # Add exchange suffix if needed
        if self.exchange == 'NSE':
            self.symbol = f"{self.original_symbol}.NS" if not self.original_symbol.endswith('.NS') else self.original_symbol
        elif self.exchange == 'BSE':
            self.symbol = f"{self.original_symbol}.BO" if not self.original_symbol.endswith('.BO') else self.original_symbol
        else:  # US or already has suffix
            self.symbol = self.original_symbol
        
        try:
            self.stock = yf.Ticker(self.symbol)
            # Quick validation
            info = self.stock.info
            if not info or 'symbol' not in info:
                raise ValueError(f"Invalid stock symbol: {symbol}")
        except Exception as e:
            raise ValueError(f"Error fetching stock {symbol} on {exchange}: {str(e)}")
    
    def get_historical_data(self, period="1y"):
        """
        Fetch historical price data
        
        Args:
            period (str): Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
        
        Returns:
            pandas.DataFrame: Historical price data with OHLCV
        """
        try:
            data = self.stock.history(period=period)
            if data.empty:
                raise ValueError(f"No historical data available for {self.symbol}")
            return data
        except Exception as e:
            raise ValueError(f"Error fetching historical data: {str(e)}")
    
    def get_fundamentals(self):
        """
        Fetch fundamental data
        
        Returns:
            dict: Dictionary of fundamental metrics
        """
        try:
            info = self.stock.info
            
            fundamentals = {
                # Valuation metrics
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                
                # Financial health
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                
                # Profitability
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                
                # Growth
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                
                # Per share metrics
                'eps': info.get('trailingEps'),
                'forward_eps': info.get('forwardEps'),
                'book_value': info.get('bookValue'),
                
                # Market data
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'beta': info.get('beta'),
                
                # Dividends
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                
                # Additional info
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'company_name': info.get('longName')
            }
            
            return fundamentals
        except Exception as e:
            print(f"Warning: Could not fetch all fundamentals: {str(e)}")
            return {}
    
    def get_current_price(self):
        """
        Get current stock price
        
        Returns:
            float: Current price
        """
        try:
            data = self.stock.history(period='1d')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except:
            return None
    
    def get_company_info(self):
        """
        Get basic company information
        
        Returns:
            dict: Company information
        """
        try:
            info = self.stock.info
            return {
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'website': info.get('website'),
                'description': info.get('longBusinessSummary')
            }
        except:
            return {}

    def is_valid(self):
        """
        Check if stock symbol is valid
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            info = self.stock.info
            return bool(info and 'symbol' in info)
        except:
            return False
