"""
Stock symbol database for autocomplete
"""

NSE_STOCKS = {
    'RELIANCE': 'Reliance Industries Ltd.',
    'TCS': 'Tata Consultancy Services Ltd.',
    'HDFCBANK': 'HDFC Bank Ltd.',
    'INFY': 'Infosys Ltd.',
    'ICICIBANK': 'ICICI Bank Ltd.',
    'HINDUNILVR': 'Hindustan Unilever Ltd.',
    'SBIN': 'State Bank of India',
    'BHARTIARTL': 'Bharti Airtel Ltd.',
    'KOTAKBANK': 'Kotak Mahindra Bank Ltd.',
    'ITC': 'ITC Ltd.',
    'LT': 'Larsen & Toubro Ltd.',
    'AXISBANK': 'Axis Bank Ltd.',
    'ASIANPAINT': 'Asian Paints Ltd.',
    'MARUTI': 'Maruti Suzuki India Ltd.',
    'TATAMOTORS': 'Tata Motors Ltd.',
    'SUNPHARMA': 'Sun Pharmaceutical Industries Ltd.',
    'WIPRO': 'Wipro Ltd.',
    'ONGC': 'Oil & Natural Gas Corporation Ltd.',
    'NTPC': 'NTPC Ltd.',
    'POWERGRID': 'Power Grid Corporation of India Ltd.',
    'ULTRACEMCO': 'UltraTech Cement Ltd.',
    'BAJFINANCE': 'Bajaj Finance Ltd.',
    'M&M': 'Mahindra & Mahindra Ltd.',
    'TECHM': 'Tech Mahindra Ltd.',
    'TITAN': 'Titan Company Ltd.',
    'ADANIPORTS': 'Adani Ports and Special Economic Zone Ltd.',
    'DRREDDY': 'Dr. Reddy\'s Laboratories Ltd.',
    'CIPLA': 'Cipla Ltd.',
    'DIVISLAB': 'Divi\'s Laboratories Ltd.',
    'NESTLEIND': 'Nestle India Ltd.',
    'BRITANNIA': 'Britannia Industries Ltd.',
    'HEROMOTOCO': 'Hero MotoCorp Ltd.',
    'EICHERMOT': 'Eicher Motors Ltd.',
    'JSWSTEEL': 'JSW Steel Ltd.',
    'TATASTEEL': 'Tata Steel Ltd.',
    'HINDALCO': 'Hindalco Industries Ltd.',
    'COALINDIA': 'Coal India Ltd.',
    'GRASIM': 'Grasim Industries Ltd.',
    'BAJAJFINSV': 'Bajaj Finserv Ltd.',
    'HCLTECH': 'HCL Technologies Ltd.',
    'INDUSINDBK': 'IndusInd Bank Ltd.',
    'ADANIENT': 'Adani Enterprises Ltd.',
    'TATACONSUM': 'Tata Consumer Products Ltd.',
    'SHRIRAMFIN': 'Shriram Finance Ltd.',
    'APOLLOHOSP': 'Apollo Hospitals Enterprise Ltd.',
    'DLF': 'DLF Ltd.',
    'PIDILITIND': 'Pidilite Industries Ltd.',
    'HAVELLS': 'Havells India Ltd.',
    'GODREJCP': 'Godrej Consumer Products Ltd.',
    'DABUR': 'Dabur India Ltd.',
    'VEDL': 'Vedanta Ltd.',
}

BSE_STOCKS = {
    'RELIANCE': 'Reliance Industries Ltd.',
    'TCS': 'Tata Consultancy Services Ltd.',
    'HDFCBANK': 'HDFC Bank Ltd.',
    'INFY': 'Infosys Ltd.',
    'ICICIBANK': 'ICICI Bank Ltd.',
    # Add more BSE stocks as needed
}

US_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc. (Google)',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'NVDA': 'NVIDIA Corporation',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'WMT': 'Walmart Inc.',
    'JNJ': 'Johnson & Johnson',
    'PG': 'Procter & Gamble Co.',
    'MA': 'Mastercard Inc.',
    'HD': 'Home Depot Inc.',
    'BAC': 'Bank of America Corp.',
    'XOM': 'Exxon Mobil Corporation',
    'CVX': 'Chevron Corporation',
    'ABBV': 'AbbVie Inc.',
    'KO': 'Coca-Cola Company',
    'PEP': 'PepsiCo Inc.',
}

def get_stocks_by_exchange(exchange):
    """Get stock dictionary by exchange"""
    if exchange == 'NSE':
        return NSE_STOCKS
    elif exchange == 'BSE':
        return BSE_STOCKS
    else:
        return US_STOCKS

def search_stocks(query, exchange):
    """
    Search stocks by symbol or name
    
    Args:
        query (str): Search query
        exchange (str): Exchange code
    
    Returns:
        list: List of matching stocks
    """
    stocks = get_stocks_by_exchange(exchange)
    query = query.upper().strip()
    
    if not query:
        return []
    
    matches = []
    
    # Search by symbol (prefix match)
    for symbol, name in stocks.items():
        if symbol.startswith(query):
            matches.append((symbol, name))
    
    # Search by name (contains match)
    for symbol, name in stocks.items():
        if query in name.upper() and (symbol, name) not in matches:
            matches.append((symbol, name))
    
    return matches[:10]  # Return top 10 matches

def format_stock_display(symbol, name):
    """Format stock for display"""
    return f"{symbol} - {name}"
