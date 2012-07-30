#from util import HTMLFetcher, Configuration
from crawler import Crawler, CrawlCandidate
from extractor import StandardContentExtractor
from util import HTMLFetcher, Configuration
def main():
    url = 'http://localhost/projects/pyGoose/target.html'
    #url = 'http://www.google.co.in'
    config = Configuration()
    #parsing config as param to crawlcandidate maynot be 
    config.contentextractor = StandardContentExtractor
    crawlcandidate = CrawlCandidate(config,url)

    crawler = Crawler(config)
    article = crawler.crawl(crawlcandidate)

    print (article.title)
    print (article.rawDoc)
    #todo 

    #create artile - test article attributes
    
if __name__ == '__main__':
    main()
