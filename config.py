"""
Configuration file for stock analysis rules
Customize these parameters based on your investment strategy
"""

# Rule-based system for different holding periods
RULES = {
    "week": {
        # Weights determine importance of each factor (must sum to 1.0)
        "weights": {
            "technical": 0.70,    # 70% weight on technical indicators
            "fundamental": 0.20,   # 20% weight on fundamentals
            "momentum": 0.10       # 10% weight on momentum
        },
        
        # Thresholds for technical indicators
        "thresholds": {
            "rsi_oversold": 30,        # RSI below this = oversold (buy signal)
            "rsi_overbought": 70,      # RSI above this = overbought (sell signal)
            "volume_spike": 1.5,       # Volume 1.5x average = significant
            "macd_strength": 0.5       # MACD signal strength threshold
        },
        
        # Which indicators to prioritize
        "priority_indicators": ["RSI", "MACD", "Volume", "Short_MA"],
        
        # Minimum confidence level to recommend
        "min_confidence": 60
    },
    
    "month": {
        "weights": {
            "technical": 0.50,     # Balanced approach
            "fundamental": 0.30,
            "momentum": 0.20
        },
        
        "thresholds": {
            "rsi_oversold": 35,
            "rsi_overbought": 65,
            "volume_spike": 1.3,
            "pe_undervalued": 15,      # P/E ratio below this = undervalued
            "pe_overvalued": 30,       # P/E ratio above this = overvalued
            "support_level": 0.95      # Price near support (95% of recent low)
        },
        
        "priority_indicators": ["RSI", "MACD", "Volume", "MA_Crossover", "PE_Ratio"],
        
        "min_confidence": 55
    },
    
    "long_term": {
        "weights": {
            "technical": 0.20,     # Fundamentals matter most for long-term
            "fundamental": 0.60,
            "momentum": 0.20
        },
        
        "thresholds": {
            "peg_undervalued": 1.0,      # PEG < 1 = undervalued growth stock
            "peg_overvalued": 2.0,
            "pe_undervalued": 15,
            "pe_overvalued": 35,
            "roe_excellent": 0.20,       # ROE > 20% = excellent
            "roe_good": 0.15,            # ROE > 15% = good
            "debt_equity_excellent": 0.3, # Debt/Equity < 0.3 = excellent
            "debt_equity_good": 0.5,     # Debt/Equity < 0.5 = good
            "profit_margin_good": 0.10,  # Profit margin > 10% = good
            "revenue_growth_good": 0.10  # Revenue growth > 10% = good
        },
        
        "priority_indicators": ["PE_Ratio", "PEG_Ratio", "ROE", "Debt_to_Equity", "Profit_Margins"],
        
        "min_confidence": 50
    }
}

# Signal scoring system
SIGNAL_SCORES = {
    "BUY": 1.0,
    "STRONG_BUY": 1.5,
    "HOLD": 0.0,
    "SELL": -1.0,
    "STRONG_SELL": -1.5
}

# Risk tolerance settings
RISK_LEVELS = {
    "conservative": {
        "min_confidence": 70,
        "require_fundamentals": True
    },
    "moderate": {
        "min_confidence": 60,
        "require_fundamentals": False
    },
    "aggressive": {
        "min_confidence": 50,
        "require_fundamentals": False
    }
}
