"""
Utility functions for the stock analyzer
"""
from datetime import datetime

def validate_inputs(symbol, holding_term):
    """
    Validate user inputs
    
    Args:
        symbol (str): Stock symbol
        holding_term (str): Holding term
    
    Returns:
        dict: Validation result
    """
    if not symbol or not isinstance(symbol, str):
        return {'valid': False, 'error': 'Stock symbol is required'}
    
    if len(symbol) > 10:
        return {'valid': False, 'error': 'Stock symbol too long'}
    
    valid_terms = ['week', 'month', 'long_term']
    if holding_term not in valid_terms:
        return {
            'valid': False, 
            'error': f"Holding term must be one of: {', '.join(valid_terms)}"
        }
    
    return {'valid': True}


def format_currency(value):
    """Format number as currency"""
    if value is None:
        return "N/A"
    
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:.2f}"


def format_percentage(value):
    """Format number as percentage"""
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def format_number(value, decimals=2):
    """Format number with specified decimals"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def get_signal_emoji(signal):
    """Get emoji for signal type"""
    emoji_map = {
        'BUY': '🟢',
        'STRONG_BUY': '🟢🟢',
        'SELL': '🔴',
        'STRONG_SELL': '🔴🔴',
        'HOLD': '🟡',
        'STRONG': '💪',
        'WEAK': '📉',
        'NORMAL': '➖'
    }
    return emoji_map.get(signal, '⚪')


def format_output(results):
    """
    Format and print analysis results
    
    Args:
        results (dict): Analysis results
    """
    print("\n" + "="*60)
    print("  ANALYSIS RESULTS")
    print("="*60)
    
    # Company info
    print(f"\n📊 Company: {results.get('company_name', 'N/A')}")
    print(f"🏷️  Symbol: {results['symbol']}")
    
    current_price = results.get('current_price')
    if current_price:
        print(f"💰 Current Price: ${current_price:.2f}")
    
    company_info = results.get('company_info', {})
    if company_info.get('sector'):
        print(f"🏭 Sector: {company_info['sector']}")
    if company_info.get('industry'):
        print(f"🏢 Industry: {company_info['industry']}")
    
    # Decision
    decision = results['decision']
    print(f"\n{'='*60}")
    print(f"  RECOMMENDATION")
    print(f"{'='*60}")
    
    decision_emoji = get_signal_emoji(decision['decision'])
    print(f"\n{decision_emoji} Decision: {decision['decision']}")
    print(f"📊 Confidence: {decision['confidence']:.1f}%")
    print(f"⏱️  Holding Term: {results['holding_term'].replace('_', ' ').title()}")
    
    # Confidence threshold check
    if decision['meets_threshold']:
        print(f"✅ Confidence meets minimum threshold ({decision['min_confidence']}%)")
    else:
        print(f"⚠️  Confidence below minimum threshold ({decision['min_confidence']}%)")
        print(f"   Recommendation: Wait for clearer signals")
    
    # Reasoning
    print(f"\n📋 Reasoning:")
    for reason in decision['reasoning']:
        print(f"   • {reason}")
    
    # Scores
    scores = decision['scores']
    print(f"\n📈 Score Breakdown:")
    print(f"   Technical Score: {scores['technical_score']:.2f}")
    print(f"   Fundamental Score: {scores['fundamental_score']:.2f}")
    print(f"   Overall Score: {scores['overall_score']:.2f}")
    
    # Signal counts
    signal_counts = decision['signal_counts']
    print(f"\n📊 Signal Distribution:")
    print(f"   🟢 Buy Signals: {signal_counts['buy']}")
    print(f"   🔴 Sell Signals: {signal_counts['sell']}")
    print(f"   🟡 Hold/Neutral: {signal_counts['hold']}")
    print(f"   📝 Total Signals: {signal_counts['total']}")
    
    # Technical indicators
    print(f"\n{'='*60}")
    print(f"  TECHNICAL INDICATORS")
    print(f"{'='*60}")
    
    for signal in results['technical_signals']:
        emoji = get_signal_emoji(signal.get('signal', ''))
        indicator = signal.get('indicator', 'Unknown')
        signal_type = signal.get('signal', 'N/A')
        description = signal.get('description', '')
        
        print(f"\n{emoji} {indicator}: {signal_type}")
        if description:
            print(f"   {description}")
        
        # Print specific values
        if 'value' in signal:
            print(f"   Value: {signal['value']}")
    
    # Fundamental indicators
    if results['fundamental_signals']:
        print(f"\n{'='*60}")
        print(f"  FUNDAMENTAL INDICATORS")
        print(f"{'='*60}")
        
        for signal in results['fundamental_signals']:
            emoji = get_signal_emoji(signal.get('signal', ''))
            indicator = signal.get('indicator', 'Unknown')
            signal_type = signal.get('signal', 'N/A')
            description = signal.get('description', '')
            
            print(f"\n{emoji} {indicator}: {signal_type}")
            if description:
                print(f"   {description}")
            
            # Print specific values
            if 'value' in signal:
                value = signal['value']
                print(f"   Value: {value}")
            
            # Print details for financial health
            if indicator == 'Financial_Health' and 'details' in signal:
                print(f"   Details:")
                for detail in signal['details']:
                    print(f"      • {detail}")
    
    # Disclaimer
    print(f"\n{'='*60}")
    print(f"  DISCLAIMER")
    print(f"{'='*60}")
    print("\n⚠️  This analysis is for informational purposes only.")
    print("   NOT financial advice. Always do your own research.")
    print("   Past performance does not guarantee future results.")
    print("   Consult a financial advisor before making investment decisions.")
    
    print(f"\n{'='*60}\n")


def print_technical_details(signals):
    """Print detailed technical analysis"""
    print("\n" + "="*60)
    print("  DETAILED TECHNICAL ANALYSIS")
    print("="*60)
    
    for signal in signals:
        print(f"\n{signal.get('indicator', 'Unknown')}:")
        for key, value in signal.items():
            if key not in ['indicator', 'description']:
                print(f"  {key}: {value}")


def print_fundamental_details(signals):
    """Print detailed fundamental analysis"""
    print("\n" + "="*60)
    print("  DETAILED FUNDAMENTAL ANALYSIS")
    print("="*60)
    
    for signal in signals:
        print(f"\n{signal.get('indicator', 'Unknown')}:")
        for key, value in signal.items():
            if key not in ['indicator', 'description']:
                print(f"  {key}: {value}")
