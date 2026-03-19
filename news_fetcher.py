"""
News fetcher for Indian stock market - Smart Priority System
Fetches news in order: Stock-specific → Peer → Sector → Global
Filters by timeframe based on holding period
"""
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import pandas as pd
import time
import re

class IndianMarketNewsFetcher:
    """Fetches real-time news from Indian financial sources with smart priority"""
    
    def __init__(self):
        self.sources = {
            'moneycontrol': 'https://www.moneycontrol.com/rss/latestnews.xml',
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'business_standard': 'https://www.business-standard.com/rss/latest.rss',
            'livemint': 'https://www.livemint.com/rss/markets'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Peer companies mapping (for peer news)
        self.peer_mapping = {
            'IOC': ['BPCL', 'HPCL', 'Reliance', 'oil', 'petroleum', 'refinery'],
            'RELIANCE': ['IOC', 'BPCL', 'HPCL', 'petrochemical', 'energy'],
            'TCS': ['Infosys', 'Wipro', 'HCL Tech', 'Tech Mahindra', 'IT services'],
            'INFY': ['TCS', 'Wipro', 'HCL Tech', 'Tech Mahindra', 'IT services'],
            'HDFCBANK': ['ICICI Bank', 'Axis Bank', 'Kotak', 'SBI', 'banking'],
            'ICICIBANK': ['HDFC Bank', 'Axis Bank', 'Kotak', 'SBI', 'banking'],
            'TATAMOTORS': ['Maruti', 'Mahindra', 'Hyundai', 'automobile', 'auto'],
            'MARUTI': ['Tata Motors', 'Mahindra', 'Hyundai', 'automobile', 'auto'],
        }
        
        # Sector keywords
        self.sector_keywords = {
            'Technology': ['tech', 'IT', 'software', 'digital', 'cloud', 'AI'],
            'Financials': ['bank', 'finance', 'lending', 'NBFC', 'insurance'],
            'Financial Services': ['bank', 'finance', 'lending', 'NBFC', 'insurance'],
            'Healthcare': ['pharma', 'health', 'drug', 'medicine', 'hospital', 'vaccine'],
            'Energy': ['oil', 'gas', 'power', 'energy', 'petroleum', 'renewable'],
            'Consumer Defensive': ['FMCG', 'consumer goods', 'retail', 'food'],
            'Consumer Cyclical': ['auto', 'automobile', 'car', 'consumer durables'],
            'Basic Materials': ['steel', 'metal', 'cement', 'mining', 'commodity'],
            'Industrials': ['manufacturing', 'industrial', 'infrastructure', 'construction'],
            'Communication Services': ['telecom', 'telecommunication', 'communication'],
            'Utilities': ['power', 'electricity', 'utility', 'gas distribution']
        }
        
        # Global news keywords
        self.global_keywords = ['Fed', 'Federal Reserve', 'China', 'US market', 'crude oil', 
                               'gold', 'dollar', 'global', 'international', 'world economy',
                               'trade war', 'inflation', 'interest rate', 'recession']
    
    def parse_news_date(self, date_str):
        """Parse news date and return datetime object"""
        try:
            # Handle various date formats
            if 'ago' in date_str.lower():
                # "2 hours ago", "1 day ago"
                if 'hour' in date_str:
                    hours = int(re.search(r'\d+', date_str).group())
                    return datetime.now() - timedelta(hours=hours)
                elif 'day' in date_str:
                    days = int(re.search(r'\d+', date_str).group())
                    return datetime.now() - timedelta(days=days)
                elif 'minute' in date_str:
                    return datetime.now()
                else:
                    return datetime.now() - timedelta(days=1)
            elif 'just now' in date_str.lower() or 'latest' in date_str.lower():
                return datetime.now()
            else:
                # Try parsing standard date formats
                for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%d', '%d %b %Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
                # If all fails, assume recent
                return datetime.now() - timedelta(hours=12)
        except:
            return datetime.now() - timedelta(hours=12)
    
    def is_within_timeframe(self, news_date, holding_term):
        """Check if news is within acceptable timeframe for holding term"""
        now = datetime.now()
        
        if holding_term == 'week':
            max_age = timedelta(days=2)  # Last 2 days for weekly
        elif holding_term == 'month':
            max_age = timedelta(days=30)  # Last 30 days for monthly
        else:  # long_term
            max_age = timedelta(days=60)  # Last 60 days for long-term
        
        # If news_date is timezone-aware, make now timezone-aware too
        if news_date.tzinfo is not None:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        age = now - news_date
        return age <= max_age
    
    def scrape_moneycontrol_latest(self):
        """Scrape latest news from Moneycontrol"""
        try:
            url = 'https://www.moneycontrol.com/news/business/markets/'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            headlines = []
            news_items = soup.find_all('li', class_='clearfix')[:15]
            
            for item in news_items:
                title_tag = item.find('h2') or item.find('a')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.find('a')['href'] if title_tag.find('a') else ''
                    
                    time_tag = item.find('span', class_='article_schedule')
                    time_text = time_tag.get_text(strip=True) if time_tag else 'Just now'
                    
                    headlines.append({
                        'title': title,
                        'source': 'moneycontrol',
                        'published': time_text,
                        'published_date': self.parse_news_date(time_text),
                        'link': link if link.startswith('http') else f'https://www.moneycontrol.com{link}'
                    })
            
            return headlines
        except Exception as e:
            print(f"Could not scrape Moneycontrol: {e}")
            return []
    
    def scrape_economic_times_latest(self):
        """Scrape latest news from Economic Times"""
        try:
            url = 'https://economictimes.indiatimes.com/markets'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            headlines = []
            news_items = soup.find_all('div', class_='eachStory')[:15]
            
            for item in news_items:
                title_tag = item.find('h3') or item.find('a')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link_tag = item.find('a')
                    link = link_tag['href'] if link_tag else ''
                    
                    time_tag = item.find('time') or item.find('span', class_='time')
                    time_text = time_tag.get_text(strip=True) if time_tag else 'Recent'
                    
                    headlines.append({
                        'title': title,
                        'source': 'economic_times',
                        'published': time_text,
                        'published_date': self.parse_news_date(time_text),
                        'link': link if link.startswith('http') else f'https://economictimes.indiatimes.com{link}'
                    })
            
            return headlines
        except Exception as e:
            print(f"Could not scrape Economic Times: {e}")
            return []
    
    def get_rss_feed_news(self):
        """Get news from RSS feeds (fallback)"""
        try:
            all_headlines = []
            
            for source_name, rss_url in self.sources.items():
                try:
                    feed = feedparser.parse(rss_url)
                    for entry in feed.entries[:10]:
                        pub_date = self.parse_news_date(entry.get('published', ''))
                        all_headlines.append({
                            'title': entry.title,
                            'source': source_name,
                            'published': entry.get('published', 'N/A'),
                            'published_date': pub_date,
                            'link': entry.get('link', '')
                        })
                except Exception as e:
                    continue
            
            return all_headlines
        except Exception as e:
            print(f"Error fetching RSS feeds: {e}")
            return []
    
    def get_all_news(self, holding_term='week'):
        """Get all news and filter by timeframe"""
        all_headlines = []
        
        # Scrape real-time news
        all_headlines.extend(self.scrape_moneycontrol_latest())
        time.sleep(1)
        all_headlines.extend(self.scrape_economic_times_latest())
        
        # Fallback to RSS
        if len(all_headlines) < 10:
            all_headlines.extend(self.get_rss_feed_news())
        
        # Filter by timeframe
        filtered = [h for h in all_headlines if self.is_within_timeframe(h['published_date'], holding_term)]
        
        # Remove duplicates
        seen = set()
        unique = []
        for h in filtered:
            if h['title'] not in seen:
                seen.add(h['title'])
                unique.append(h)
        
        return unique
    
    def get_stock_specific_news(self, symbol, company_name, holding_term='week'):
        """
        Get news with priority: Stock-specific → Peer → Sector → Global
        
        Args:
            symbol: Stock symbol (e.g., 'IOC', 'RELIANCE')
            company_name: Full company name
            holding_term: 'week', 'month', or 'long_term'
        """
        print(f"\n🔍 Searching news for {symbol} ({holding_term})...")
        
        all_news = self.get_all_news(holding_term)
        
        # Priority 1: Stock-specific news
        stock_specific = []
        company_variations = [
            symbol.upper(),
            company_name.lower() if company_name else '',
            company_name.split()[0].lower() if company_name else ''
        ]
        
        for news in all_news:
            title_lower = news['title'].lower()
            # Exact match for symbol (case-insensitive, whole word)
            if re.search(r'\b' + re.escape(symbol.lower()) + r'\b', title_lower):
                stock_specific.append({**news, 'priority': 'Stock-Specific'})
            # Company name match
            elif company_name and any(var in title_lower for var in company_variations if var):
                stock_specific.append({**news, 'priority': 'Stock-Specific'})
        
        print(f"  ✓ Found {len(stock_specific)} stock-specific news")
        
        # Priority 2: Peer news (if stock-specific < 3)
        peer_news = []
        if len(stock_specific) < 3:
            peers = self.peer_mapping.get(symbol, [])
            for news in all_news:
                if news not in stock_specific:
                    title_lower = news['title'].lower()
                    if any(peer.lower() in title_lower for peer in peers):
                        peer_news.append({**news, 'priority': 'Peer'})
            
            print(f"  ✓ Found {len(peer_news)} peer company news")
        
        # Priority 3: Sector news (if total < 5)
        sector_news = []
        if len(stock_specific) + len(peer_news) < 5:
            # Determine sector (you'll need to pass this or detect it)
            sector_keywords = self.get_sector_keywords_for_symbol(symbol)
            for news in all_news:
                if news not in stock_specific and news not in peer_news:
                    title_lower = news['title'].lower()
                    if any(keyword.lower() in title_lower for keyword in sector_keywords):
                        sector_news.append({**news, 'priority': 'Sector'})
            
            print(f"  ✓ Found {len(sector_news)} sector news")
        
        # Priority 4: Global news (always include top 2-3)
        global_news = []
        for news in all_news:
            if news not in stock_specific and news not in peer_news and news not in sector_news:
                title_lower = news['title'].lower()
                if any(keyword.lower() in title_lower for keyword in self.global_keywords):
                    global_news.append({**news, 'priority': 'Global'})
        
        print(f"  ✓ Found {len(global_news)} global market news")
        
        # Combine with priority
        result = (
            stock_specific[:5] +  # Max 5 stock-specific
            peer_news[:3] +       # Max 3 peer
            sector_news[:3] +     # Max 3 sector
            global_news[:2]       # Always 2 global
        )
        
        print(f"  📰 Total relevant news: {len(result)}\n")
        
        return result[:10]  # Return max 10 total
    
    def get_sector_keywords_for_symbol(self, symbol):
        """Get sector keywords for a symbol"""
        # This is a simplified mapping - you can enhance it
        sector_map = {
            'IOC': ['oil', 'petroleum', 'energy', 'fuel'],
            'BPCL': ['oil', 'petroleum', 'energy', 'fuel'],
            'HPCL': ['oil', 'petroleum', 'energy', 'fuel'],
            'RELIANCE': ['oil', 'petrochemical', 'energy', 'telecom'],
            'TCS': ['IT', 'tech', 'software', 'digital'],
            'INFY': ['IT', 'tech', 'software', 'digital'],
            'WIPRO': ['IT', 'tech', 'software', 'digital'],
            'HDFCBANK': ['bank', 'finance', 'lending', 'NBFC'],
            'ICICIBANK': ['bank', 'finance', 'lending', 'NBFC'],
            'TATAMOTORS': ['auto', 'automobile', 'car', 'EV'],
            'MARUTI': ['auto', 'automobile', 'car'],
        }
        
        return sector_map.get(symbol, ['market', 'stock'])
    
    def get_market_sentiment(self, holding_term='week'):
        """Get overall Indian market sentiment from latest news"""
        try:
            all_headlines = self.get_all_news(holding_term)
            
            if not all_headlines:
                return {
                    'sentiment': 'neutral',
                    'headlines': [],
                    'score': 0,
                    'positive_count': 0,
                    'negative_count': 0
                }
            
            # Sentiment analysis
            positive_keywords = ['surge', 'rally', 'gain', 'jump', 'rise', 'high', 'bullish', 
                               'growth', 'profit', 'strong', 'up', 'boost', 'record', 'soar',
                               'advance', 'climb', 'positive', 'upbeat', 'optimistic']
            negative_keywords = ['fall', 'drop', 'crash', 'loss', 'decline', 'down', 'weak',
                               'bearish', 'slump', 'plunge', 'concern', 'warning', 'risk',
                               'tumble', 'slide', 'dip', 'negative', 'worry', 'fear']
            
            positive_count = 0
            negative_count = 0
            
            for headline in all_headlines:
                title_lower = headline['title'].lower()
                if any(word in title_lower for word in positive_keywords):
                    positive_count += 1
                if any(word in title_lower for word in negative_keywords):
                    negative_count += 1
            
            total = positive_count + negative_count
            if total == 0:
                sentiment = 'neutral'
                score = 0
            else:
                sentiment_score = (positive_count - negative_count) / total
                if sentiment_score > 0.2:
                    sentiment = 'bullish'
                    score = sentiment_score
                elif sentiment_score < -0.2:
                    sentiment = 'bearish'
                    score = sentiment_score
                else:
                    sentiment = 'neutral'
                    score = sentiment_score
            
            return {
                'sentiment': sentiment,
                'score': score,
                'headlines': all_headlines[:20],
                'positive_count': positive_count,
                'negative_count': negative_count
            }
        
        except Exception as e:
            print(f"Error fetching market sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'headlines': [],
                'score': 0,
                'positive_count': 0,
                'negative_count': 0
            }
    
    def get_sectoral_news(self, sector, holding_term='week'):
        """Get news specific to a sector"""
        try:
            keywords = self.sector_keywords.get(sector, [sector.lower()])
            all_news = self.get_all_news(holding_term)
            
            relevant_headlines = []
            
            for headline in all_news:
                title_lower = headline['title'].lower()
                if any(keyword.lower() in title_lower for keyword in keywords):
                    relevant_headlines.append(headline)
            
            if not relevant_headlines:
                return {'sentiment': 'neutral', 'headlines': []}
            
            # Analyze sentiment
            positive_keywords = ['surge', 'rally', 'gain', 'jump', 'rise', 'bullish', 'growth', 'strong', 'boost']
            negative_keywords = ['fall', 'drop', 'crash', 'loss', 'decline', 'bearish', 'slump', 'weak', 'concern']
            
            positive = sum(1 for h in relevant_headlines 
                          if any(word in h['title'].lower() for word in positive_keywords))
            negative = sum(1 for h in relevant_headlines 
                          if any(word in h['title'].lower() for word in negative_keywords))
            
            total = positive + negative
            if total == 0:
                sentiment = 'neutral'
            elif positive > negative:
                sentiment = 'bullish'
            else:
                sentiment = 'bearish'
            
            return {
                'sentiment': sentiment,
                'headlines': relevant_headlines[:10],
                'positive': positive,
                'negative': negative
            }
        
        except Exception as e:
            print(f"Error fetching sectoral news: {e}")
            return {'sentiment': 'neutral', 'headlines': []}
