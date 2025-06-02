import requests
from bs4 import BeautifulSoup
import threading
import time
from queue import Queue
import signal
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsItem:
    """Simple data class for news items"""
    def __init__(self, name: str, title: str, desc: str, timestamp: str):
        # Input validation - fixes Issue #8
        if not all([name, title, desc, timestamp]):
            raise ValueError("All fields must be non-empty")
        self.name = name
        self.title = title
        self.desc = desc
        self.timestamp = timestamp


class HTTPClient:
    """Handles HTTP requests with timeout and retry - fixes Issue #4"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def fetch(self, url: str) -> Optional[str]:
        """Fetch content with timeout and retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Add timeout to prevent hanging - fixes Issue #4
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout attempt {attempt + 1} for {url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                break
            
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def close(self):
        """Close session"""
        self.session.close()


class NewsParser(ABC):
    """Base parser class - fixes Issue #5 (code duplication)"""
    
    @abstractmethod
    def parse(self, html_content: str) -> List[NewsItem]:
        pass
    
    def safe_get_text(self, element) -> str:
        """Safely extract text - fixes Issue #1 (NoneType errors)"""
        if element is None:
            return ""
        return element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
    
    def safe_get_attr(self, element, attr: str) -> str:
        """Safely extract attribute - fixes Issue #1 (NoneType errors)"""
        if element is None:
            return ""
        return element.get(attr, "") if hasattr(element, 'get') else ""


class Liputan6Parser(NewsParser):
    """Parser for Liputan6 website"""
    
    def parse(self, html_content: str) -> List[NewsItem]:
        news_items = []
        try:
            soup = BeautifulSoup(html_content, features="html.parser")
            website_name = self._get_site_name(soup)
            
            for news in soup.find_all('div', class_="headline--main__wrapper"):
                try:
                    title_elem = news.find('h1', class_="headline--main__title")
                    desc_elem = news.find('p', class_="headline--main__short-desc")
                    time_elem = news.find('time', class_="timeago")
                    
                    # Use safe extraction methods - fixes Issue #1
                    title = self.safe_get_text(title_elem)
                    desc = self.safe_get_text(desc_elem)
                    timestamp = self.safe_get_attr(time_elem, "datetime")
                    
                    if title and desc and timestamp:
                        news_items.append(NewsItem(website_name, title, desc, timestamp))
                except Exception as e:
                    logger.warning(f"Error parsing news item: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error parsing Liputan6 content: {e}")
        
        return news_items
    
    def _get_site_name(self, soup) -> str:
        try:
            if soup.head and soup.head.find('title'):
                return soup.head.find('title').string or "Liputan6"
        except:
            pass
        return "Liputan6"


class BisnisParser(NewsParser):
    """Parser for Bisnis website"""
    
    def parse(self, html_content: str) -> List[NewsItem]:
        news_items = []
        try:
            soup = BeautifulSoup(html_content, features="html.parser")
            website_name = self._get_site_name(soup)
            
            for news in soup.find_all('li', class_="big style2"):
                try:
                    # Safe nested element access - fixes Issue #1
                    channel_elem = news.find('div', class_="channel")
                    date_elem = channel_elem.find('div', class_="date") if channel_elem else None
                    
                    h2_elem = news.find('h2')
                    title_link = h2_elem.find('a', class_="bigteks") if h2_elem else None
                    
                    desc_elem = news.find('div', class_="description")
                    
                    # Use safe extraction methods - fixes Issue #1
                    timestamp = self.safe_get_text(date_elem)
                    title = self.safe_get_attr(title_link, 'title')
                    desc = self.safe_get_text(desc_elem)
                    
                    if title and desc and timestamp:
                        news_items.append(NewsItem(website_name, title, desc, timestamp))
                except Exception as e:
                    logger.warning(f"Error parsing news item: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error parsing Bisnis content: {e}")
        
        return news_items
    
    def _get_site_name(self, soup) -> str:
        try:
            if soup.head and soup.head.find('title'):
                return soup.head.find('title').string or "Bisnis"
        except:
            pass
        return "Bisnis"


class ABCParser(NewsParser):
    """Parser for ABC News website"""
    
    def parse(self, html_content: str) -> List[NewsItem]:
        news_items = []
        try:
            soup = BeautifulSoup(html_content, features="html.parser")
            website_name = self._get_site_name(soup)
            
            selector = 'div[data-id="103068804"].GenericCard_card__oqpe3'
            for news in soup.select(selector):
                try:
                    title_elem = news.find('a', class_="GenericCard_link__EMXqX")
                    desc_elem = news.find('div', class_="Typography_base__sj2RP GenericCard_synopsis__mgnzs")
                    time_elem = news.find('time', class_="Typography_base__sj2RP DynamicTimestamp_printDate__OVPa2")
                    
                    # Use safe extraction methods - fixes Issue #1
                    title = self.safe_get_text(title_elem)
                    desc = self.safe_get_text(desc_elem)
                    timestamp = self.safe_get_text(time_elem)
                    
                    if title and desc and timestamp:
                        news_items.append(NewsItem(website_name, title, desc, timestamp))
                except Exception as e:
                    logger.warning(f"Error parsing news item: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error parsing ABC content: {e}")
        
        return news_items
    
    def _get_site_name(self, soup) -> str:
        try:
            if soup.head and soup.head.find('title'):
                return soup.head.find('title').string or "ABC News"
        except:
            pass
        return "ABC News"


class NewsScraping:
    """Main scraper class - fixes Issue #2 (separation of concerns)"""
    
    def __init__(self, news_site: str, interval: int):
        # Input validation - fixes Issue #8
        if not news_site or interval <= 0:
            raise ValueError("Invalid parameters")
        
        self.news_site = news_site
        self.interval = interval
        self.news_queue = Queue()
        self.stop_event = threading.Event()
        
        # Separate HTTP client - fixes Issue #2, #4
        self.http_client = HTTPClient()
        
        # Use factory pattern for parsers - fixes Issue #3
        self.parser = self._create_parser()
        self.thread = None
    
    def _create_parser(self) -> NewsParser:
        """Factory method for creating parsers - fixes Issue #3"""
        if self.news_site == "https://www.liputan6.com/":
            return Liputan6Parser()
        elif self.news_site == "https://www.bisnis.com/":
            return BisnisParser()
        elif self.news_site == "https://www.abc.net.au/news/indonesian":
            return ABCParser()
        else:
            raise ValueError("Unsupported news site")
    
    def fetch(self) -> Optional[str]:
        """Fetch content using HTTP client"""
        return self.http_client.fetch(self.news_site)
    
    def scrape_news(self):
        """Main scraping loop with better error handling - fixes Issue #7"""
        while not self.stop_event.is_set():
            try:
                html_content = self.fetch()
                if html_content:
                    news_data = self.parser.parse(html_content)
                    for news_item in news_data:
                        if not self.stop_event.is_set():
                            self.news_queue.put(news_item)
                
                # Interruptible sleep - fixes Issue #6
                for _ in range(self.interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error scraping {self.news_site}: {e}")
                time.sleep(5)  # Wait before retry
    
    def start_thread(self):
        """Start scraping thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("Thread already running")
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.scrape_news, daemon=True)
        self.thread.start()
        logger.info(f"Started thread for {self.news_site}")
    
    def stop_thread(self):
        """Stop scraping thread properly - fixes Issue #6"""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Thread did not stop gracefully")
        logger.info(f"Stopped thread for {self.news_site}")


def main_thread(news_scrapers):
    """Main aggregation function"""
    seen_news = set()
    
    try:
        while not all(scraper.stop_event.is_set() for scraper in news_scrapers):
            for scraper in news_scrapers:
                while not scraper.news_queue.empty():
                    try:
                        news = scraper.news_queue.get_nowait()
                        news_tuple = (news.name, news.title, news.desc, news.timestamp)
                        
                        if news_tuple not in seen_news:
                            print(f"Website Name: {news.name}")
                            print(f"News Title: {news.title}")
                            print(f"Description: {news.desc}")
                            print(f"Time Posted: {news.timestamp}")
                            print("=" * 50)
                            seen_news.add(news_tuple)
                    except:
                        break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        # Proper cleanup - fixes Issue #6
        for scraper in news_scrapers:
            scraper.stop_thread()
            scraper.http_client.close()


if __name__ == '__main__':
    # Create scrapers with error handling
    scrapers = []
    
    configs = [
        ("https://www.liputan6.com/", 3600),
        ("https://www.bisnis.com/", 1800),
        ("https://www.abc.net.au/news/indonesian", 900)
    ]
    
    for url, interval in configs:
        try:
            scraper = NewsScraping(url, interval)
            scrapers.append(scraper)
            scraper.start_thread()
        except Exception as e:
            logger.error(f"Failed to create scraper for {url}: {e}")
    
    # Setup signal handler for graceful shutdown - fixes Issue #6
    def signal_handler(signum, frame):
        logger.info("Shutting down...")
        for scraper in scrapers:
            scraper.stop_thread()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run main loop
    if scrapers:
        main_thread(scrapers) 