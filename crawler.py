from html.parser import HTMLParser
from util import URLHelper, HTMLFetcher, getouterhtml
from cleaner import DocumentCleaner
import logging
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.FileHandler('./log/crawl.log'))
class Article(object):
    """docstring for Article"""
    def __init__(self):
        super(Article, self).__init__()
    
        
#class Configuration(object):
#    """docstring for Configuration"""
#    def __init__(self, arg):
#        super(Configuration, self).__init__()
#        self.arg = arg
        
class CrawlCandidate(object):
    """docstring for CrawlCandidate"""
    def __init__(self, config, url, rawHTMl = None):
        super(CrawlCandidate, self).__init__()
        self.config = config
        self.url = url
        self.rawHTMl = rawHTMl
        
class Crawler(object):
    """docstring for Crawler"""
    def __init__(self, config):
        super(Crawler, self).__init__()
        self.config = config

    
    def crawl(self, crawlcandidate):

        article = Article()
        # take input url, parse it
        urlhelper = URLHelper()
        parsecandidate = urlhelper.getcleanedurl(crawlcandidate.url)
        rawHTML = self.getHTML(crawlcandidate, parsecandidate)  
        if rawHTML  :
            doc = self.get_document(parsecandidate, rawHTML)
            logging.info("Crawling from " + crawlcandidate.url)
            #extractor = self.config.contentextractor
            extractor = self.get_extractor()
            article = Article()
            article.finalurl = parsecandidate.url
            article.linkhash = parsecandidate.linkhash
            article.rawHTML = rawHTML
            article.doc = doc
            import copy
            #to check if this is necessary , to do a shallow or a deepcopy
            article.rawDoc = copy.deepcopy(doc)
            article.title = extractor.gettitle(article.doc)
            article.publishdate = self.get_publishdatextr().extract(article.doc)
            #article.additiondata = config.additiondataextractor.extract(article.doc)
            article.metadesc = extractor.getmetadesc(article.doc)
            article.metakeywords = extractor.getmetakeywords(article.doc)
            article.canonicallink = extractor.getcanonicallink(article.doc)
            if not article.canonicallink: article.canonicallink = article.finalurl

            article.domain = extractor.getdomain(article.finalurl)
            article.tags = extractor.extracttags(article.doc)

            #clean up the document
            cleaner = self.get_doccleaner()
            cleaner.clean(article)
            #get highest weighted nodes
            topnode = extractor.getbestnodes_bsdoncluster(article.doc)

            #print(type(title.ownerDocument))
            if topnode is not None:
                article.topnode = topnode
                #extract video and images
                logging.info("TOPNODE " + getouterhtml(topnode))
                article.topnode = extractor.postextractionclean(topnode)
                logging.debug("POST EXTRACT \n" + getouterhtml(topnode))
                formatter = self.get_formatter()
                article.cleanedtext = formatter.getformattedtext(article.topnode)
                logging.debug(article.cleanedtext)
            else:
                logging.info("NO ARTICLE FOUND")
            return article
        else :
            logging.info("Document at " + crawlcandidate.url + " is empty")
        

    def getHTML(self, crawlcandidate, parsecandidate):
        if crawlcandidate.rawHTMl:
            return crawlcandidate.rawHTMl
        else:
            fetcher = HTMLFetcher()
            return fetcher.getHTML(self.config, parsecandidate)


    def get_document(self, parsecandidate, rawHTML):
        #print(type(rawHTML))
        if not isinstance(rawHTML,str):
            #decode bytes to HTML string
            decodedHTML = None
            try:            
                #detect coding with BeautifulSoup 4
                from bs4 import UnicodeDammit
                ud = UnicodeDammit(rawHTML,[],None, True)
                decodedHTML = ud.unicode_markup
            except ImportError as e:
                logging.warn('BeautifulSoup 4 mightnot be installed. Use default decode')
                logging.warn(str(e))

            if not decodedHTML: 
                #try fallback to str encode
                if not parsecandidate.charset: 
                    parsecandidate.charset='utf-8'
                    #print(parsecandidate.charset)
                decodedHTML = rawHTML.decode(parsecandidate.charset)

            #create DOM document    
        else:
            decodedHTML = rawHTMl   

        try:
            
            from lxml.html import fromstring            
            from lxml import etree
            doc  = fromstring(decodedHTML)
            return doc
        except etree.ParserError as e:
            logging.error(str(e))
            logging.info('Fallback to BeautifulSoup parser')
            try:
                #use beautifulsoup parser as the last resource
                from bs4 import BeautifulSoup
                from lxml.html import soupparser
                doc = soupparser.fromstring(decodedHTML,BeautifulSoup)
                return doc
            except Exception as e:
                logging.error(str(e))
                raise e
        except ImportError as e:
            logging.error(str(e))
            raise e
        except Exception as e:          
            logging.error("Unable to parse " + parsecandidate.url + " into DOM Document:" + str(e))
            raise e

    def get_extractor(self):
        if not hasattr(self,'contentextractor'):
            self.contentextractor = self.config.contentextractor(self.config)
        return self.contentextractor

    def get_publishdatextr(self):
        if not hasattr(self, 'publishdatextr'):
            self.publishdatextr = self.config.pubdateextractor()
        return self.publishdatextr

    def get_doccleaner(self):
        if not hasattr(self, 'cleaner'):
            self.cleaner = self.config.doccleaner(self.config)
        return self.cleaner 

    def get_formatter(self):
        if not hasattr(self, 'formatter'):
            self.formatter = self.config.formatter(self.config)
        return self.formatter







