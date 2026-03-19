"""
Rule engine module - applies predefined rules to make buy/hold/sell decisions
"""
from config import RULES, SIGNAL_SCORES

class RuleEngine:
    """Applies rules to technical and fundamental signals to make trading decisions"""
    
    def __init__(self, holding_term):
        """
        Initialize rule engine with holding term
        
        Args:
            holding_term (str): 'week', 'month', or 'long_term'
        """
        if holding_term not in RULES:
            raise ValueError(f"Invalid holding term: {holding_term}. Must be 'week', 'month', or 'long_term'")
        
        self.holding_term = holding_term
        self.config = RULES[holding_term]
        self.weights = self.config['weights']
        self.thresholds = self.config['thresholds']
        self.priority_indicators = self.config.get('priority_indicators', [])
        self.min_confidence = self.config.get('min_confidence', 50)
    
    def calculate_technical_score(self, technical_signals):
        """
        Calculate weighted score from technical signals
        
        Args:
            technical_signals (list): List of technical indicator results
        
        Returns:
            float: Technical score
        """
        if not technical_signals:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for signal in technical_signals:
            if 'signal' not in signal:
                continue
            
            # Get signal value
            signal_value = signal['signal']
            
            # Convert to numeric score
            if signal_value == 'BUY':
                score = 1.0
            elif signal_value == 'SELL':
                score = -1.0
            elif signal_value == 'STRONG':
                score = 0.5  # For volume
            elif signal_value == 'WEAK':
                score = -0.5
            else:  # HOLD or other
                score = 0
            
            # Apply priority weighting
            indicator_name = signal.get('indicator', '')
            if indicator_name in self.priority_indicators:
                weight = 1.5  # 50% more weight for priority indicators
            else:
                weight = 1.0
            
            total_score += score * weight
            total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0
        
        return normalized_score
    
    def calculate_fundamental_score(self, fundamental_signals):
        """
        Calculate weighted score from fundamental signals
        
        Args:
            fundamental_signals (list): List of fundamental indicator results
        
        Returns:
            float: Fundamental score
        """
        if not fundamental_signals:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for signal in fundamental_signals:
            if 'signal' not in signal:
                continue
            
            # Get signal value
            signal_value = signal['signal']
            
            # Convert to numeric score
            if signal_value == 'BUY':
                score = 1.0
            elif signal_value == 'SELL':
                score = -1.0
            else:  # HOLD
                score = 0
            
            # Special weighting for financial health (it's comprehensive)
            indicator_name = signal.get('indicator', '')
            if indicator_name == 'Financial_Health':
                # Use the health score directly
                health_score = signal.get('score', 0)
                if health_score >= 4:
                    score = 1.0
                elif health_score >= 2:
                    score = 0.75
                elif health_score <= -4:
                    score = -1.0
                elif health_score <= -2:
                    score = -0.75
                else:
                    score = 0
                weight = 2.0  # Financial health gets double weight
            elif indicator_name in self.priority_indicators:
                weight = 1.5
            else:
                weight = 1.0
            
            total_score += score * weight
            total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0
        
        return normalized_score
    
    def calculate_overall_score(self, technical_signals, fundamental_signals):
        """
        Calculate overall weighted score
        
        Args:
            technical_signals (list): Technical indicator signals
            fundamental_signals (list): Fundamental indicator signals
        
        Returns:
            dict: Scores breakdown
        """
        # Calculate individual scores
        tech_score = self.calculate_technical_score(technical_signals)
        fund_score = self.calculate_fundamental_score(fundamental_signals)
        
        # Apply holding term weights
        weighted_tech = tech_score * self.weights['technical']
        weighted_fund = fund_score * self.weights['fundamental']
        
        # Calculate overall score (-1 to +1)
        overall_score = weighted_tech + weighted_fund
        
        return {
            'technical_score': round(tech_score, 3),
            'fundamental_score': round(fund_score, 3),
            'weighted_technical': round(weighted_tech, 3),
            'weighted_fundamental': round(weighted_fund, 3),
            'overall_score': round(overall_score, 3)
        }
    
    def make_decision(self, technical_signals, fundamental_signals):
        """
        Make final buy/hold/sell decision
        
        Args:
            technical_signals (list): Technical indicator signals
            fundamental_signals (list): Fundamental indicator signals
        
        Returns:
            dict: Final decision with confidence and reasoning
        """
        # Calculate scores
        scores = self.calculate_overall_score(technical_signals, fundamental_signals)
        overall_score = scores['overall_score']
        
        # Determine decision based on overall score
        if overall_score > 0.3:
            decision = 'BUY'
            confidence_base = 50 + (overall_score * 50)  # 50-100%
        elif overall_score < -0.3:
            decision = 'SELL'
            confidence_base = 50 + (abs(overall_score) * 50)  # 50-100%
        else:
            decision = 'HOLD'
            confidence_base = 50 + (30 - abs(overall_score * 100))  # 50-80%
        
        # Calculate confidence (0-100%)
        confidence = min(100, max(0, confidence_base))
        
        # Count supporting signals
        buy_signals = sum(1 for s in technical_signals + fundamental_signals 
                         if s.get('signal') == 'BUY')
        sell_signals = sum(1 for s in technical_signals + fundamental_signals 
                          if s.get('signal') == 'SELL')
        hold_signals = sum(1 for s in technical_signals + fundamental_signals 
                          if s.get('signal') == 'HOLD')
        total_signals = buy_signals + sell_signals + hold_signals
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            decision, 
            scores, 
            buy_signals, 
            sell_signals, 
            hold_signals,
            technical_signals,
            fundamental_signals
        )
        
        # Check if confidence meets minimum threshold
        meets_threshold = confidence >= self.min_confidence
        
        return {
            'decision': decision,
            'confidence': round(confidence, 1),
            'meets_threshold': meets_threshold,
            'min_confidence': self.min_confidence,
            'scores': scores,
            'signal_counts': {
                'buy': buy_signals,
                'sell': sell_signals,
                'hold': hold_signals,
                'total': total_signals
            },
            'reasoning': reasoning,
            'holding_term': self.holding_term
        }
    
    def _generate_reasoning(self, decision, scores, buy_signals, sell_signals, 
                           hold_signals, technical_signals, fundamental_signals):
        """
        Generate human-readable reasoning for the decision
        
        Returns:
            list: List of reasoning points
        """
        reasoning = []
        
        # Overall assessment
        if decision == 'BUY':
            reasoning.append(f"📈 Overall analysis suggests a buying opportunity")
        elif decision == 'SELL':
            reasoning.append(f"📉 Overall analysis suggests selling or avoiding")
        else:
            reasoning.append(f"⏸️ Mixed signals suggest waiting for clearer direction")
        
        # Signal distribution
        reasoning.append(f"Signals: {buy_signals} bullish, {sell_signals} bearish, {hold_signals} neutral")
        
        # Technical analysis summary
        tech_score = scores['technical_score']
        if tech_score > 0.5:
            reasoning.append(f"✓ Strong positive technical indicators")
        elif tech_score > 0.2:
            reasoning.append(f"✓ Moderately positive technical indicators")
        elif tech_score < -0.5:
            reasoning.append(f"✗ Strong negative technical indicators")
        elif tech_score < -0.2:
            reasoning.append(f"✗ Moderately negative technical indicators")
        else:
            reasoning.append(f"≈ Neutral technical indicators")
        
        # Fundamental analysis summary
        fund_score = scores['fundamental_score']
        if self.holding_term == 'long_term':
            if fund_score > 0.5:
                reasoning.append(f"✓ Strong fundamentals support long-term growth")
            elif fund_score > 0.2:
                reasoning.append(f"✓ Decent fundamentals for long-term holding")
            elif fund_score < -0.5:
                reasoning.append(f"✗ Weak fundamentals raise concerns")
            elif fund_score < -0.2:
                reasoning.append(f"✗ Fundamentals show some weaknesses")
        
        # Highlight key signals
        strong_buy_signals = [s for s in technical_signals + fundamental_signals 
                             if s.get('signal') == 'BUY' and 
                             s.get('indicator') in self.priority_indicators]
        
        strong_sell_signals = [s for s in technical_signals + fundamental_signals 
                              if s.get('signal') == 'SELL' and 
                              s.get('indicator') in self.priority_indicators]
        
        if strong_buy_signals:
            indicators = ', '.join(s.get('indicator', '') for s in strong_buy_signals[:2])
            reasoning.append(f"Key bullish signals from: {indicators}")
        
        if strong_sell_signals:
            indicators = ', '.join(s.get('indicator', '') for s in strong_sell_signals[:2])
            reasoning.append(f"Key bearish signals from: {indicators}")
        
        return reasoning
    
    def get_rule_summary(self):
        """
        Get summary of current rules being applied
        
        Returns:
            dict: Rule configuration summary
        """
        return {
            'holding_term': self.holding_term,
            'weights': self.weights,
            'priority_indicators': self.priority_indicators,
            'min_confidence': self.min_confidence,
            'thresholds': self.thresholds
        }
