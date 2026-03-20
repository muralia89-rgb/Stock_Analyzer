"""
News fetching module for stock-specific news
"""
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import time

class NewsFetcher:
    """Fetch stock-specific news from multiple sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_stock_news(self, symbol, company_name=None, sector=None, timeframe='week'):
        """
        Fetch news specific to a stock with fallback hierarchy
        
        Args:
            symbol (str): Stock ticker symbol (e.g., 'RELIANCE', 'TCS')
            company_name (str): Full company name (e.g., 'Reliance Industries')
            sector (str): Company sector (e.g., 'Energy', 'Technology')
            timeframe (str): 'week', 'month', or 'long'
        
        Returns:
            list: News articles with titles, links, dates, and relevance
        """
        print(f"\n📰 Fetching news for {symbol}...")
        
        all_news = []
        
        # Priority 1: Stock-specific news
        stock_news = self._fetch_stock_specific_news(symbol, company_name)
        if stock_news:
            print(f"✓ Found {len(stock_news)} stock-specific articles")
            all_news.extend(stock_news)
        
        # Priority 2: Sector news (if not enough stock news)
        if len(all_news) < 5 and sector and sector != 'Unknown':
            sector_news = self._fetch_sector_news(sector)
            if sector_news:
                print(f"✓ Found {len(sector_news)} sector-related articles")
                all_news.extend(sector_news)
        
        # Priority 3: General market news (fallback)
        if len(all_news) < 3:
            market_news = self._fetch_general_market_news()
            if market_news:
                print(f"✓ Found {len(market_news)} general market articles")
                all_news.extend(market_news)
        
        # Filter by timeframe
        filtered_news = self._filter_by_timeframe(all_news, timeframe)
        
        # Remove duplicates
        unique_news = self._remove_duplicates(filtered_news)
        
        print(f"📊 Total relevant news: {len(unique_news)}")
        return unique_news[:10]  # Return top 10
    
    def _fetch_stock_specific_news(self, symbol, company_name=None):
        """Fetch news specifically about this stock"""
        news = []
        
        # Try multiple sources
        sources = [
            self._search_moneycontrol,
            self._search_economic_times,
            self._search_livemint,
            self._search_business_standard
        ]
        
        for source_func in sources:
            try:
                source_news = source_func(symbol, company_name)
                if source_news:
                    news.extend(source_news)
            except Exception as e:
                print(f"⚠️ {source_func.__name__} failed: {e}")
                continue
        
        return news
    
    def _search_moneycontrol(self, symbol, company_name=None):
        """Search Moneycontrol for stock-specific news"""
        try:
            # Use company name if available, otherwise symbol
            search_term = company_name if company_name else symbol
            search_term = search_term.replace(' ', '+')
            
            url = f'https://www.moneycontrol.com/news/news-all/{search_term}'
            
            response = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('li', class_='clearfix')
            
            for article in articles[:5]:
                try:
                    title_tag = article.find('h2') or article.find('a')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag.find('a')['href'] if title_tag.find('a') else title_tag.get('href', '')
                    
                    # Check if article is relevant to the stock
                    if self._is_relevant(title, symbol, company_name):
                        news_items.append({
                            'title': title,
                            'link': link,
                            'source': 'Moneycontrol',
                            'date': datetime.now(),
                            'relevance': 'stock-specific'
                        })
                except:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Moneycontrol search error: {e}")
            return []
    
    def _search_economic_times(self, symbol, company_name=None):
        """Search Economic Times for stock-specific news"""
        try:
            search_term = company_name if company_name else symbol
            search_term = search_term.replace(' ', '+')
            
            url = f'https://economictimes.indiatimes.com/topic/{search_term}'
            
            response = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('div', class_='eachStory')
            
            for article in articles[:5]:
                try:
                    title_tag = article.find('h3') or article.find('a')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    link_tag = article.find('a')
                    link = link_tag['href'] if link_tag else ''
                    
                    if not link.startswith('http'):
                        link = 'https://economictimes.indiatimes.com' + link
                    
                    if self._is_relevant(title, symbol, company_name):
                        news_items.append({
                            'title': title,
                            'link': link,
                            'source': 'Economic Times',
                            'date': datetime.now(),
                            'relevance': 'stock-specific'
                        })
                except:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Economic Times search error: {e}")
            return []
    
    def _search_livemint(self, symbol, company_name=None):
        """Search LiveMint for stock-specific news"""
        try:
            search_term = company_name if company_name else symbol
            
            # LiveMint RSS feed for companies
            url = f'https://www.livemint.com/rss/companies'
            
            feed = feedparser.parse(url)
            news_items = []
            
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    link = entry.link
                    
                    # Check relevance
                    if self._is_relevant(title, symbol, company_name):
                        pub_date = entry.get('published_parsed', None)
                        if pub_date:
                            pub_date = datetime(*pub_date[:6])
                        else:
                            pub_date = datetime.now()
                        
                        news_items.append({
                            'title': title,
                            'link': link,
                            'source': 'LiveMint',
                            'date': pub_date,
                            'relevance': 'stock-specific'
                        })
                except:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"LiveMint search error: {e}")
            return []
    
    def _search_business_standard(self, symbol, company_name=None):
        """Search Business Standard for stock-specific news"""
        try:
            search_term = company_name if company_name else symbol
            search_term = search_term.replace(' ', '-').lower()
            
            url = f'https://www.business-standard.com/topic/{search_term}'
            
            response = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            articles = soup.find_all('div', class_='listing-txt')
            
            for article in articles[:5]:
                try:
                    title_tag = article.find('a')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    
                    if not link.startswith('http'):
                        link = 'https://www.business-standard.com' + link
                    
                    if self._is_relevant(title, symbol, company_name):
                        news_items.append({
                            'title': title,
                            'link': link,
                            'source': 'Business Standard',
                            'date': datetime.now(),
                            'relevance': 'stock-specific'
                        })
                except:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Business Standard search error: {e}")
            return []
    
    def _fetch_sector_news(self, sector):
        """Fetch news about the sector/industry"""
        try:
            sector_keywords = {
                'Technology': ['IT', 'software', 'technology', 'tech'],
                'Financial Services': ['banking', 'finance', 'NBFC', 'insurance'],
                'Energy': ['oil', 'gas', 'energy', 'petroleum', 'power'],
                'Healthcare': ['pharma', 'healthcare', 'medical', 'drugs'],
                'Consumer': ['FMCG', 'consumer', 'retail'],
                'Automobile': ['auto', 'automobile', 'cars', 'vehicles'],
                'Telecom': ['telecom', 'telecommunications', '5G', 'spectrum']
            }
            
            keywords = sector_keywords.get(sector, [sector.lower()])
            news_items = []
            
            # Search Moneycontrol sector news
            for keyword in keywords[:2]:
                try:
                    url = f'https://www.moneycontrol.com/news/business/stocks/'
                    response = requests.get(url, headers=self.headers, timeout=5, verify=False)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles = soup.find_all('li', class_='clearfix')[:5]
                        
                        for article in articles:
                            try:
                                title_tag = article.find('h2') or article.find('a')
                                if title_tag and keyword.lower() in title_tag.get_text().lower():
                                    title = title_tag.get_text(strip=True)
                                    link = title_tag.find('a')['href'] if title_tag.find('a') else ''
                                    
                                    news_items.append({
                                        'title': title,
                                        'link': link,
                                        'source': 'Moneycontrol',
                                        'date': datetime.now(),
                                        'relevance': 'sector'
                                    })
                            except:
                                continue
                except:
                    continue
            
            return news_items[:5]
            
        except Exception as e:
            print(f"Sector news error: {e}")
            return []
    
    def _fetch_general_market_news(self):
        """Fetch general market news (fallback)"""
        try:
            url = 'https://www.moneycontrol.com/rss/MCtopnews.xml'
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:
                try:
                    news_items.append({
                        'title': entry.title,
                        'link': entry.link,
                        'source': 'Moneycontrol',
                        'date': datetime.now(),
                        'relevance': 'general'
                    })
                except:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"General news error: {e}")
            return []
    
    def _is_relevant(self, title, symbol, company_name=None):
        """Check if news title is relevant to the stock"""
        title_lower = title.lower()
        
        # Check for symbol
        if symbol.lower() in title_lower:
            return True
        
        # Check for company name
        if company_name:
            company_words = company_name.lower().split()
            # Check if at least 2 words from company name appear
            matches = sum(1 for word in company_words if len(word) > 3 and word in title_lower)
            if matches >= 2 or (len(company_words) == 1 and company_words[0] in title_lower):
                return True
        
        return False
    
    def _filter_by_timeframe(self, news_list, timeframe):
        """Filter news by timeframe"""
        if timeframe == 'week':
            cutoff = datetime.now() - timedelta(days=7)
        elif timeframe == 'month':
            cutoff = datetime.now() - timedelta(days=30)
        else:  # long-term
            cutoff = datetime.now() - timedelta(days=60)
        
        filtered = []
        for article in news_list:
            if article.get('date'):
                if article['date'] >= cutoff:
                    filtered.append(article)
            else:
                # Include if no date (assume recent)
                filtered.append(article)
        
        return filtered
    
    def _remove_duplicates(self, news_list):
        """Remove duplicate news articles"""
        seen_titles = set()
        unique_news = []
        
        for article in news_list:
            title_normalized = article['title'].lower().strip()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_news.append(article)
        
        return unique_news
    
    def get_news_summary(self, news_list):
        """Get a summary of news sentiment and key themes"""
        if not news_list:
            return {
                'total_articles': 0,
                'stock_specific': 0,
                'sector_related': 0,
                'general_market': 0,
                'sources': []
            }
        
        summary = {
            'total_articles': len(news_list),
            'stock_specific': len([n for n in news_list if n.get('relevance') == 'stock-specific']),
            'sector_related': len([n for n in news_list if n.get('relevance') == 'sector']),
            'general_market': len([n for n in news_list if n.get('relevance') == 'general']),
            'sources': list(set([n.get('source', 'Unknown') for n in news_list]))
        }
        
        return summary
