"""
Advanced sentiment analysis for news headlines
"""
from textblob import TextBlob
import re

class NewsSentimentAnalyzer:
    """Analyze sentiment from news headlines"""
    
    def __init__(self):
        self.positive_words = [
            'surge', 'rally', 'gain', 'jump', 'rise', 'high', 'bullish',
            'growth', 'profit', 'strong', 'up', 'boost', 'record', 'soar',
            'advance', 'climb', 'positive', 'upbeat', 'optimistic', 'beat',
            'exceed', 'outperform', 'upgrade', 'buy', 'recommend'
        ]
        
        self.negative_words = [
            'fall', 'drop', 'crash', 'loss', 'decline', 'down', 'weak',
            'bearish', 'slump', 'plunge', 'concern', 'warning', 'risk',
            'tumble', 'slide', 'dip', 'negative', 'worry', 'fear',
            'miss', 'disappoint', 'downgrade', 'sell', 'avoid'
        ]
    
    def analyze_headline(self, headline):
        """Analyze single headline sentiment"""
        headline_lower = headline.lower()
        
        # Count positive/negative words
        positive_count = sum(1 for word in self.positive_words if word in headline_lower)
        negative_count = sum(1 for word in self.negative_words if word in headline_lower)
        
        # TextBlob sentiment
        try:
            blob = TextBlob(headline)
            polarity = blob.sentiment.polarity  # -1 to 1
        except:
            polarity = 0
        
        # Combined score
        word_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        combined_score = (word_score + polarity) / 2
        
        if combined_score > 0.2:
            sentiment = 'positive'
        elif combined_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': combined_score,
            'confidence': abs(combined_score)
        }
    
    def analyze_multiple(self, headlines):
        """Analyze multiple headlines"""
        if not headlines:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = [self.analyze_headline(h['title']) for h in headlines]
        
        positive = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        
        if avg_score > 0.15:
            overall = 'positive'
        elif avg_score < -0.15:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': avg_score,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'confidence': abs(avg_score)
        }
```

Add to `requirements.txt`:
```
textblob
