import logging
import re
import extractor
from lxml import etree
import text
import cleaner

def replacewithtext(node):
    """replace an element with its text """
    parent = node.getparent()
    #parent.remove(node)
    #nodetext  = node.text
    #if node.tail is not None:
    #    nodetext = nodetext + node.tail if nodetext else node.tail
    #nodetext = nodetext.strip()
    nodetext = getinnertext(node, True)
    if nodetext is not None:
        logging.info("replace " + node.tag + " with text " + nodetext)
        prevsib = node.getprevious()#next(node.itersiblings(preceding=True))
        if prevsib is not None:
            prevsib.tail = prevsib.tail + nodetext if prevsib.tail else nodetext
        else:
            #prevsib.tail = prevsib.tail.strip()
            parent.text = parent.text + nodetext if parent.text is not None else nodetext
    parent.remove(node)

def inspectgroup(elegroup):
    """ utility to print out a group of element nodes"""
    for node in elegroup:
        logging.debug("Element %s " % node.tag)

def getouterhtml(node):
    """return outerhtml of a node as string"""
    tail = node.tail
    node.tail = None
    outerhtml = etree.tostring(node).decode('utf-8')
    node.tail = tail
    return outerhtml

def getinnerhtml(node, ):
    """ inner html of a node """ 
    text = node.text 
    for child in node.iterchildren():
        text = text + getouterhtml(child) if text else getouterhtml(child) 
        if child.tail:
            text = text+child.tail if text else child.tail
    return text

def getinnertext(node, includeChildren = False):
    """ get inner text """
    # when includeChildren is set to True, text of child node is included
    # set includeChildren to True when the result text is used to check if the node is trivial(removeable) or not
    # set it to False when text is used to score node to avoid double weighing for a text in case of <p> inside <p>
    text = node.text 
    for child in node.iterchildren():
        if includeChildren:
            #if child.text:
            childtext = getinnertext(child, True)
            if childtext:
                text = childtext if not text else text + childtext
        else:
            # only add for non-blk tag like <a>, <b>, <i>, <strong>
            config = Configuration()
            if child.tag in config.nonblktags and child.text:
                text = child.text if not text else text + child.text
        if child.tail is not None:
            text = child.tail if not text else text + child.tail
    return text

class Configuration(object):
    """hold settings for crawling process"""
    (STOPWORD_BASED, WORDCOUNT_BASED) = (0,1)

    def __init__(self):
        super(Configuration, self).__init__()
        self.headers = { 
                    'accept-language': 'en-us,en;q=0.5', 
                    'dnt': '1', 'keep-alive': '115', 
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1', 
                    'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        }
        #instead of storing instances of extractors in config object
        # as Jim Goose does, we only keep classnames here 
        # as we believe config object should only serve as a reference 
        # for other operations rather than the tool itself
        self.pubdateextractor = extractor.PublishDateExtractor
        self.contentextractor = extractor.ContentExtractor
        self.doccleaner = cleaner.DocumentCleaner
        # set of tags that can be inside a paragarah, to decorate text, link ...
        # these tags should be considered part of a bigger paragraph
        self.nonblktags = ["a","b","i","strong"]
        # formatter to clean up text after extraction
        self.formatter = text.Formatter
        self.texthandler = text.TextHandler

from urllib.request import urlopen, Request
from exception import NotFoundException

class HTMLFetcher(object):
    """docstring for HTMLFetcher"""
    def __init__(self):
        super(HTMLFetcher, self).__init__()

    
    def getHTML(self,config,parsecandidate):
        hashChar = parsecandidate.url.find('#')
        if(hashChar>=0):
            url = parsecandidate.url[0:hashChar]
        else:
            url = parsecandidate.url

        try:
            #empty cookie store?
            #get http response
            request = Request(url,None, config.headers)
            response = urlopen(request)
            if response.getcode() == 404:
                raise NotFoundException(url)
            #find character encode
            contenttype = response.getheader('content-type')
            csidx = contenttype.find('charset')
            if contenttype and csidx :
                parsecandidate.charset = contenttype[csidx + len('charset='):]
                parsecandidate.charset = parsecandidate.charset.strip()

            return response.readall()
        except NotFoundException as e:
            logging.error("Link not found (404): " + e.url) 
            raise e
        except Exception as e:
            raise e

class ParsingCandidate(object):
    """docstring for ParsingCandidate"""
    def __init__(self, urlstr, linkhash, url):
        super(ParsingCandidate, self).__init__()

        self.urlstr  = urlstr   
        self.linkhash = linkhash
        self.url = url

from hashlib import md5
class URLHelper(object):
    """docstring for URLHelper"""
    def __init__(self):
        super(URLHelper, self).__init__()
    

    def getcleanedurl(self, url):
        """the use of a cleaned url is not obvious now, let see """
        try:
            if(url.find('#!')>=0):
                clearnUrl = re.sub(r'#!', r'?_escaped_fragment=',url)
            else:
                clearnUrl = url

            return ParsingCandidate(clearnUrl, md5(url.encode('utf-8')), url)
        except Exception as e:
            logging.critical("Error in parsing url " + str(url))
            raise e


