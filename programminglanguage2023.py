import requests
from bs4 import BeautifulSoup
import threading
import time
from queue import Queue
import signal

class NewsScraping:
    def __init__(self, news_site, interval):
        self.news_site = news_site
        self.interval = interval
        self.news_queue = Queue()
        self.stop_event = threading.Event()

    def fetch(self):
        try:
            response = requests.get(self.news_site)
            response.raise_for_status() 
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetch website : {self.news_site}: {e}")
            return None

    def scrape_news(self):
        while not self.stop_event.is_set():
            try:
                html_content = self.fetch()
                if html_content:
                    news_data = self.scrape_site(html_content)
                    for news_item in news_data:
                        self.news_queue.put(news_item)
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error scraping {self.news_site}: {e}")

    def scrape_site(self, htmlcontent):
        if self.news_site == "https://www.liputan6.com/":
            return self.scrapenews1(htmlcontent)
        elif self.news_site == "https://www.bisnis.com/":
            return self.scrapenews2(htmlcontent)
        elif self.news_site == "https://www.abc.net.au/news/indonesian":
            return self.scrapenews3(htmlcontent)
        else:
            raise ValueError("News site not available")
        
        
    def scrapenews1(self,htmlcontent):
        datanews = []
        soup = BeautifulSoup(htmlcontent,features="html.parser")   
        if soup.head:    
            websitename = soup.head.find('title').string
        
        for news in soup.find_all('div', class_ = "headline--main__wrapper"):
            title = news.find('h1',class_="headline--main__title")
            textdesc = news.find('p', class_="headline--main__short-desc")
            timestamp = news.find('time',class_="timeago").get("datetime")
                
            datanews.append({
                'name' :websitename,
                'title': title.text,
                'desc': textdesc.text,
                'timestamp': timestamp,})
        return datanews

    def scrapenews2(self,htmlcontent):
        datanews = []
        soup = BeautifulSoup(htmlcontent,features="html.parser")
        if soup.head:    
            websitename = soup.head.find('title').string
               
        for news in soup.find_all('li', class_ = "big style2"):
            timestamp = news.find('div',class_="channel").find('div',class_="date").text
            title = news.find('h2').find('a',class_="bigteks").get('title')
            textdesc = news.find('div',class_="description").text
           
            datanews.append({'name' :websitename,'title': title,
                'desc': textdesc,
                'timestamp': timestamp,})
            
        return datanews
    
    def scrapenews3(self,htmlcontent):
        datanews = []
        soup = BeautifulSoup(htmlcontent,features="html.parser")     
        if soup.head:    
            websitename = soup.head.find('title').string
        
        for news in soup.find_all('div', attrs={'data-id':'103068804'},class_="GenericCard_card__oqpe3 CardList_item__5mvGa CardList_bordered__S40xg"):
            title = news.find('a',class_="GenericCard_link__EMXqX Link_link__5eL5m ScreenReaderOnly_srLinkHint__OysWz Link_showVisited__C1Fea Link_showFocus__ALyv2 Link_underlineNone__To6aJ")
            textdesc = news.find('div',class_="Typography_base__sj2RP GenericCard_synopsis__mgnzs Typography_sizeMobile14__u7TGe Typography_lineHeightMobile24__crkfh Typography_regular__WeIG6 Typography_colourInherit__dfnUx")
            timestamp = news.find('time', class_="Typography_base__sj2RP DynamicTimestamp_printDate__OVPa2 Typography_sizeMobile12__w_FPC Typography_lineHeightMobile20___U7Vr Typography_regular__WeIG6 Typography_colourInherit__dfnUx Typography_letterSpacedSm__V8kil")
            
            datanews.append({'name' :websitename,'title': title.text,
                'desc': textdesc.text,
                'timestamp': timestamp.text,})
            
            
        return datanews    
        

    def start_thread(self):
        thread = threading.Thread(target=self.scrape_news)
        thread.daemon = True  
        thread.start()

    def stop_thread(self):
        self.stop_event.set()

def main_thread(news_scrapers):
    seen_news = set()
    while not all(scraper.stop_event.is_set() for scraper in news_scrapers):
        for scraper in news_scrapers:
            while not scraper.news_queue.empty():
                news = scraper.news_queue.get()
                tuples = (news['name'],news['title'], news['desc'], news['timestamp'])
                if tuples not in seen_news:
                    print(f"Website Name: {news['name']}")
                    print(f"News Title: {news['title']}")
                    print(f"Description: {news['desc']}")
                    print(f"Time Posted: {news['timestamp']}")
                    print("=================================")
                    seen_news.add(tuples)
        time.sleep(1)

if __name__ == '__main__':
    scraper1 = NewsScraping("https://www.liputan6.com/", 3600) 
    scraper2 = NewsScraping("https://www.bisnis.com/", 1800)  
    scraper3 = NewsScraping("https://www.abc.net.au/news/indonesian", 900) 

    scraper1.start_thread()
    scraper2.start_thread()
    scraper3.start_thread()

    signal.signal(signal.SIGINT, lambda signum, frame: exit(0))
    newsscrapers = [scraper1, scraper2, scraper3]
    main_thread(newsscrapers)
