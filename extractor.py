import logging
import text
from lxml import etree

class ContentExtractor(object):
    """docstring for ContentExtractor"""
    def __init__(self):
        super(ContentExtractor, self).__init__()
        self.xtopnodetags = etree.XPath("//*[self::p or self::td or self::pre]") 
        
    def gettitle(self, doc):
        #select title
        titleelems = doc.cssselect('title')
        if not titleelems or len(titleelems) == 0 : 
            return None

        title = titleelems[0].text
        if not title: return None

        #split title if it contains delim
        delim = ''
        if title.find('|') >= 0 :
            #split pipe
            delim = r'|'
        elif title.find('-') >= 0 :
            #split dash
            delim = r'-'
        elif title.find('»') >= 0:
            #split arrow
            delim = r'»'
        elif title.find(':') >= 0:
            #split colon
            delim = r':'

        #split and take the longest token
        if delim: 
            tokens = title.split(delim) 
            mainTitle = ''
            for tok in tokens:
                if len(tok) > len(mainTitle):
                    mainTitle = tok
            title = mainTitle
        #replace '&raquo;' in title , motley replacement
        title = title.replace('&raquo;','').replace('»','').replace('&#65533;','')
        return title

    def getmetatcontent(self, doc, metaname):
        metaElems = doc.cssselect(metaname)
        if metaElems and len(metaElems)>0:
            content = metaElems[0].get('content')
            if content : content = content.strip()
            return content
        else:
            return None


    def getmetadesc(self, doc):
        return self.getmetatcontent(doc,'meta[name=description]')

    def getmetakeywords(self,doc):
        return self.getmetatcontent(doc, 'meta[name=keywords]')

    def getcanonicallink(self,doc):
        links = doc.cssselect('link[ref=canonical]')
        if links and len(links)>0:
            href = links[0].get('href')
            if href : href = href.strip()
            return href
        #else canonical link = article.finalUrl
        return None

    def getdomain(self, url):
        from  urllib.request import Request
        return Request(url).host

    def extracttags(self, doc):
        #A_REL_TAG_SELECTOR: String = "a[rel=tag], a[href*=/tag/]"
        # using cssselect('a[href*=tag]') -> [a element href=/tag/]
        # cssselect('a[href=tag]') can't find <a href="/tag/">
        # cssselect('a[href=/tag/]') -> invalid character error
        if len(doc.getchildren()) == 0 :
            #return empty set
            return set()
        tagSet = set()
        tags = doc.cssselect('a[ref=tag]')
        if tags and len(tags) > 0:
            for t in tags:
                tagSet.add(t.text)

        tags = doc.cssselect('a[href*=tag]')
        if tags and len(tags)>0:
            for t in tags:
                tagSet.add(t.text)

        return tagSet

    def getbestnode_bsdoncluster(self, doc):
        nodes = self.getnodestocheck(doc)
        startboost = 1.0
        count = 0 
        for node in nodes:
            if node.text!= None:
                wordstats = text.StopWord.countstopwords(node.text)
               

    def getnodestocheck(self, doc):
        #tocheck = []
        #tocheck = tocheck +  doc.cssselect('p')
        #tocheck = tocheck +   doc.cssselect('pre')
        #tocheck = tocheck +  doc.cssselect('td')
        tocheck = self.xtopnodetags(doc)
        return tocheck

    def countstopword(self, nodetext):
        """count no. of stop words in a node text"""

    def ishighlinkdensity(self, node):
        """check if a node contains lots of links"""

        

class StandardContentExtractor(ContentExtractor):
    """standard extension of ContentExtractor.
        Add no new features at the moment"""

    def __init__(self):
        super(StandardContentExtractor,self).__init__()
        

class PublishDateExtractor(object):
    """docstring for PublishDateExtractor"""
    def __init__(self):
        super(PublishDateExtractor, self).__init__()
    
    #pending not yet implemented
    def extract(self, doc):
        return None


class StopWords(object):
    """docstring for StopWords"""
    def __init__(self):
        super(StopWords, self).__init__()
        self.punctuation = re.compile(r'[^\p{Ll}\p{Lu}\p{Lt}\p{Lo}\p{Nd}\p{Pc}\s]')
        self.spacesplit = re.compile(r'\s+')
        #get stop words from file 
        self.stopwords = []
        infile = open("stopwords-en.txt")
        for l in infile:
            self.stopwords.append(l)


        
    def removepunctuation(self,text):
        return self.punctuation.sub('',text)
        
    def getstopwordscount(self, content):
        if not content:
            return None
        strippedinput = self.removepunctuation(content) 
        candidate = self.spacesplit.split(strippedinput)

        isstopwords = []
        for c in candidate:
            if c in self.stopwords:
                isstopwords.append(c)

        #return wordstat
