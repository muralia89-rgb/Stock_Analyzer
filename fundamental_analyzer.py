"""
Fundamental analysis module - analyzes company fundamentals
"""

class FundamentalAnalyzer:
    """Performs fundamental analysis on company financial data"""
    
    def __init__(self, fundamentals):
        """
        Initialize with fundamental data
        
        Args:
            fundamentals (dict): Dictionary of fundamental metrics
        """
        self.data = fundamentals
        self.signals = []
    
    def analyze_valuation(self):
        """
        Analyze valuation metrics (P/E, PEG, P/B ratios)
        
        Returns:
            list: List of valuation signals
        """
        signals = []
        
        # P/E Ratio analysis
        pe = self.data.get('pe_ratio')
        if pe and pe > 0:
            if pe < 15:
                signals.append({
                    'indicator': 'PE_Ratio',
                    'value': round(pe, 2),
                    'signal': 'BUY',
                    'reason': 'undervalued',
                    'description': f'P/E of {round(pe, 2)} suggests undervaluation'
                })
            elif pe > 30:
                signals.append({
                    'indicator': 'PE_Ratio',
                    'value': round(pe, 2),
                    'signal': 'SELL',
                    'reason': 'overvalued',
                    'description': f'P/E of {round(pe, 2)} suggests overvaluation'
                })
            else:
                signals.append({
                    'indicator': 'PE_Ratio',
                    'value': round(pe, 2),
                    'signal': 'HOLD',
                    'reason': 'fair_value',
                    'description': f'P/E of {round(pe, 2)} is fairly valued'
                })
        
        # PEG Ratio analysis
        peg = self.data.get('peg_ratio')
        if peg and peg > 0:
            if peg < 1:
                signals.append({
                    'indicator': 'PEG_Ratio',
                    'value': round(peg, 2),
                    'signal': 'BUY',
                    'reason': 'growth_undervalued',
                    'description': f'PEG of {round(peg, 2)} indicates undervalued growth'
                })
            elif peg > 2:
                signals.append({
                    'indicator': 'PEG_Ratio',
                    'value': round(peg, 2),
                    'signal': 'SELL',
                    'reason': 'growth_overvalued',
                    'description': f'PEG of {round(peg, 2)} suggests overvalued growth'
                })
            else:
                signals.append({
                    'indicator': 'PEG_Ratio',
                    'value': round(peg, 2),
                    'signal': 'HOLD',
                    'reason': 'fair_growth_value',
                    'description': f'PEG of {round(peg, 2)} is reasonable'
                })
        
        # Price to Book ratio
        pb = self.data.get('price_to_book')
        if pb and pb > 0:
            if pb < 1:
                signals.append({
                    'indicator': 'Price_to_Book',
                    'value': round(pb, 2),
                    'signal': 'BUY',
                    'reason': 'trading_below_book_value',
                    'description': f'P/B of {round(pb, 2)} - trading below book value'
                })
            elif pb > 3:
                signals.append({
                    'indicator': 'Price_to_Book',
                    'value': round(pb, 2),
                    'signal': 'SELL',
                    'reason': 'expensive_vs_book',
                    'description': f'P/B of {round(pb, 2)} is quite high'
                })
        
        return signals
    
    def analyze_financial_health(self):
        """
        Analyze financial health metrics
        
        Returns:
            dict: Financial health signal
        """
        health_score = 0
        details = []
        
        # Debt to Equity analysis
        debt_to_equity = self.data.get('debt_to_equity')
        if debt_to_equity is not None:
            debt_to_equity = debt_to_equity / 100  # Convert from percentage
            if debt_to_equity < 0.3:
                health_score += 2
                details.append('Excellent debt levels')
            elif debt_to_equity < 0.5:
                health_score += 1
                details.append('Good debt levels')
            elif debt_to_equity > 2:
                health_score -= 2
                details.append('High debt burden')
            elif debt_to_equity > 1:
                health_score -= 1
                details.append('Moderate debt levels')
        
        # Current Ratio (liquidity)
        current_ratio = self.data.get('current_ratio')
        if current_ratio:
            if current_ratio > 2:
                health_score += 2
                details.append('Excellent liquidity')
            elif current_ratio > 1.5:
                health_score += 1
                details.append('Good liquidity')
            elif current_ratio < 1:
                health_score -= 2
                details.append('Liquidity concerns')
        
        # Return on Equity (profitability)
        roe = self.data.get('roe')
        if roe:
            if roe > 0.20:
                health_score += 2
                details.append('Excellent profitability')
            elif roe > 0.15:
                health_score += 1
                details.append('Good profitability')
            elif roe < 0:
                health_score -= 2
                details.append('Unprofitable')
            elif roe < 0.05:
                health_score -= 1
                details.append('Low profitability')
        
        # Profit Margins
        profit_margin = self.data.get('profit_margins')
        if profit_margin:
            if profit_margin > 0.20:
                health_score += 1
                details.append('Strong profit margins')
            elif profit_margin < 0:
                health_score -= 1
                details.append('Negative margins')
        
        # Determine signal based on score
        if health_score >= 4:
            signal = 'BUY'
            health_status = 'excellent'
        elif health_score >= 2:
            signal = 'BUY'
            health_status = 'good'
        elif health_score <= -4:
            signal = 'SELL'
            health_status = 'poor'
        elif health_score <= -2:
            signal = 'SELL'
            health_status = 'weak'
        else:
            signal = 'HOLD'
            health_status = 'moderate'
        
        return {
            'indicator': 'Financial_Health',
            'score': health_score,
            'signal': signal,
            'status': health_status,
            'details': details,
            'description': f'Financial health is {health_status}'
        }
    
    def analyze_growth(self):
        """
        Analyze growth metrics
        
        Returns:
            list: List of growth signals
        """
        signals = []
        
        # Revenue Growth
        revenue_growth = self.data.get('revenue_growth')
        if revenue_growth:
            if revenue_growth > 0.20:
                signals.append({
                    'indicator': 'Revenue_Growth',
                    'value': round(revenue_growth * 100, 2),
                    'signal': 'BUY',
                    'description': f'Strong revenue growth of {round(revenue_growth * 100, 1)}%'
                })
            elif revenue_growth > 0.10:
                signals.append({
                    'indicator': 'Revenue_Growth',
                    'value': round(revenue_growth * 100, 2),
                    'signal': 'BUY',
                    'description': f'Good revenue growth of {round(revenue_growth * 100, 1)}%'
                })
            elif revenue_growth < 0:
                signals.append({
                    'indicator': 'Revenue_Growth',
                    'value': round(revenue_growth * 100, 2),
                    'signal': 'SELL',
                    'description': f'Negative revenue growth of {round(revenue_growth * 100, 1)}%'
                })
        
        # Earnings Growth
        earnings_growth = self.data.get('earnings_growth')
        if earnings_growth:
            if earnings_growth > 0.15:
                signals.append({
                    'indicator': 'Earnings_Growth',
                    'value': round(earnings_growth * 100, 2),
                    'signal': 'BUY',
                    'description': f'Strong earnings growth of {round(earnings_growth * 100, 1)}%'
                })
            elif earnings_growth < 0:
                signals.append({
                    'indicator': 'Earnings_Growth',
                    'value': round(earnings_growth * 100, 2),
                    'signal': 'SELL',
                    'description': f'Negative earnings growth of {round(earnings_growth * 100, 1)}%'
                })
        
        return signals
    
    def get_all_fundamental_signals(self):
        """
        Get all fundamental analysis signals
        
        Returns:
            list: List of all fundamental signals
        """
        all_signals = []
        
        # Add valuation signals
        all_signals.extend(self.analyze_valuation())
        
        # Add financial health signal
        all_signals.append(self.analyze_financial_health())
        
        # Add growth signals
        all_signals.extend(self.analyze_growth())
        
        return [s for s in all_signals if s]  # Filter out None values
