#from util import HTMLFetcher, Configuration
from crawler import Crawler, CrawlCandidate
from extractor import StandardContentExtractor
from util import HTMLFetcher, Configuration
import logging
from text import TextHandler
logging.basicConfig(level=logging.DEBUG)
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
    teststopwords()

def teststopwords():
    fi = "testsubject.txt"
    subject = open(fi)
    testtext = []
    for line in subject:
        testtext.append(line.strip())
    testtext = ' '.join(testtext)

    handle = TextHandler()
    ws = handle.getstopwordscount(testtext)
    print(ws.stopwordcount)



    
if __name__ == '__main__':
    main()
