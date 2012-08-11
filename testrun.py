#from util import HTMLFetcher, Configuration
from crawler import Crawler, CrawlCandidate
from extractor import StandardContentExtractor, LengthbsdContentExtractor
from util import HTMLFetcher, Configuration, getouterhtml, getinnertext
import logging
from text import TextHandler, LengthbsdTextHandler
logging.basicConfig(level=logging.DEBUG)
def main():
    #url = 'http://localhost/projects/pyGoose/target.html'
    url = 'http://vietnamnet.vn/vn/van-hoa/84115/xoa-an-cam-bieu-dien-voi-trong-tan-anh-tho.html'
    #url = 'http://www.google.co.in'
    config = Configuration()
    #parsing config as param to crawlcandidate maynot be 
    config.contentextractor = StandardContentExtractor
    #config.contentextractor = ContentExtractor
    #config.formatter = LengthbsdFormatter
    config.texthandler = LengthbsdTextHandler
    crawlcandidate = CrawlCandidate(config,url)

    crawler = Crawler(config)
    article = crawler.crawl(crawlcandidate)
    logging.debug(getinnertext(article.topnode, True))
    #logging.debug(getouterhtml(article.topnode))
    print (article.title)
    #todo 

    #create artile - test article attributes

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
