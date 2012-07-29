import logging
from lxml import etree
from text import TextHandler

class ContentExtractor(object):
    """docstring for ContentExtractor"""
    def __init__(self):
        super(ContentExtractor, self).__init__()
        self.xtopnodetags = etree.XPath("//*[self::p or self::td or self::pre]") 
        self.xlinks = etree.XPath("//a")
        self.texthandler = TextHandler()
        
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

    def getmetacontent(self, doc, metaname):
        metaElems = doc.cssselect(metaname)
        if metaElems and len(metaElems)>0:
            content = metaElems[0].get('content')
            if content : content = content.strip()
            return content
        else:
            return None


    def getmetadesc(self, doc):
        return self.getmetacontent(doc,'meta[name=description]')

    def getmetakeywords(self,doc):
        return self.getmetacontent(doc, 'meta[name=keywords]')

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
        if len(doc.getchildren()) == 0 :
            #return empty set
            return set()
        tagSet = set()
        tags = doc.cssselect('a[rel=tag],a[href*=tag]')
        if tags and len(tags) > 0:
            for t in tags:
                tagSet.add(t.text)

        #tags = doc.cssselect('a[href*=tag]')
        #if tags and len(tags)>0:
        #    for t in tags:
        #        tagSet.add(t.text)

        return tagSet

    def getbestnode_bsdoncluster(self, doc):
        nodeswithtext = []
        nodes = self.getnodestocheck(doc)
        startboost = 1.0
        count = 0 
        for node in nodes:
            if node.text!= None:
                wordstats = self.texthandler.getstopwordscount(node.text)
                linkdense = self.ishighlinkdensity(node)
                if(wordstats.stopwordcount > 2 and not linkdense ):
                    nodeswithtext.append(node)

        logging.info("To inspect %d nodes with text " % len(nodeswithtext))

        for node in nodeswithtext:
            boostscore = 0 
            if self.isboostable : 
                if count >= 0:
                    boostscore = 0; # to be continued

    def getnodestocheck(self, doc):
        #tocheck = []
        #tocheck = tocheck +  doc.cssselect('p')
        #tocheck = tocheck +   doc.cssselect('pre')
        #tocheck = tocheck +  doc.cssselect('td')
        tocheck = self.xtopnodetags(doc)
        return tocheck

    def ishighlinkdensity(self, node):
        """check if a node contains lots of links"""
        links = self.xlinks(node)
        if len(links) == 0: 
            return False
        text = node.text.strip()
        words = self.texthandler.splittext(text)
        linkbuffer = [] 
        for link in links:
            if link.text != None:
                linkbuffer.append(link.text)

        linktext = ' '.join(linkbuffer) 
        linkwords = self.texthandler.splittext(linktext)

        linkdivisor = len(linkwords)/len(words)
        score = linkdivisor * len(links)
        
        logging.info("Link density score is %d for node %s"%(score, self._getshortext(node)))
        return score > 1

    def _getshorttext(self,node):
        return etree.tostring(node).decode('utf-8')[:50]

    def isboostable (self, node ):
        #to be continue
        return False

        

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

