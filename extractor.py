import logging
from lxml import etree, html
from text import TextHandler
import util

class ContentExtractor(object):
    """docstring for ContentExtractor"""
    def __init__(self):
        super(ContentExtractor, self).__init__()
        self.xtopnodetags = etree.XPath("//*[self::p or self::td or self::pre]") 
        #self.xlinks = etree.XPath("./a|./*/a")
        self.texthandler = TextHandler()
        #self.xparas = etree.XPath("./p|./*/p")
        
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

    def getbestnodes_bsdoncluster(self, doc):
        nodeswithtext = []
        parentnodes = []
        nodes = self.getnodestocheck(doc)
        startboost = 1.0
        count = 0 
        i = 0 #iteration 
        for node in nodes:
            nodetext = util.getinnertext(node)
            if nodetext!= None:
                wordstats = self.texthandler.getstopwordscount(nodetext)
                linkdense = self.ishighlinkdensity(node)
                if(wordstats.stopwordcount > 2 and not linkdense ):
                    nodeswithtext.append(node)

        logging.info("To inspect %d nodes with text " % len(nodeswithtext))
        negativescore = 0
        bottomnode_for_negativescore = len(nodeswithtext) * 0.25
        for node in nodeswithtext:
            boostscore = 0 
            if self.isboostable(node) : 
                if count >= 0:
                    boostscore = ( 1.0/ startboost * 50)
                    startboost += 1
            if len(nodeswithtext) > 15:
                # for nodes that fall in bottom 25%
                if (len(nodeswithtext) - i) <= bottomnode_for_negativescore:
                    booster = bottomnode_for_negativescore - (len(nodeswithtext) - i )
                    boostscore = -math.pow(booster, 2)
                    negscore = math.abs(boostscore) + negativescore
                    if negscore > 40:
                        boostscore  = 5
            logging.debug("==========\n")
            logging.info("Location boost score %d on iteration %d id='%s' class='%s' tag='%s'" % (boostscore, i, node.getparent().get('id'), node.getparent().get('class'), node.getparent().tag ))
            
            nodetext = util.getinnertext(node) 
            logging.debug(nodetext)
            ws = self.texthandler.getstopwordscount(nodetext)
            upscore = ws.stopwordcount + boostscore
            logging.debug("total upscore = %f " % upscore ) 
            parent = node.getparent()
            grandpar = node.getparent().getparent()
            self._score(parent, upscore)
            self._score(grandpar, upscore/2)
            self._nodecount(parent, 1)
            self._nodecount(grandpar,1)
                
            try:
                parentnodes.index(parent)
            except ValueError:
                parentnodes.append(parent)

            try:
                parentnodes.index(grandpar)
            except ValueError:
                parentnodes.append(grandpar)

            count += 1
            i += 1

        topnodescore = 0
        topnode = None
        for node in parentnodes:
            logging.info("Parent Node: score=%s nodeCount=%s id=%s class=%s tag=%s" % (self._score(node),self._nodecount(node),node.get('id'),node.get('class'), node.tag))
            score = self._score(node)
            if score > topnodescore:
                topnode = node
                topnodescore = score

            if topnode is None: 
                topnode = node
        
        return topnode


    def _score(self, node, addscore=None):
        score = node.get('score')
        score = float(score) if score is not None else 0
        if addscore is not None:
            score += addscore
            node.set('score', str(score))
        return score 

    def _nodecount(self, node, addcount=None):
        count = node.get('nodecount')
        count = int(count) if count is not None else 0
        if addcount is not None:
            count += addcount
            node.set('nodecount', str(count))
        return count 


    def getnodestocheck(self, doc):
        #tocheck = []
        #tocheck = tocheck +  doc.cssselect('p')
        #tocheck = tocheck +   doc.cssselect('pre')
        #tocheck = tocheck +  doc.cssselect('td')
        tocheck = self.xtopnodetags(doc)
        return tocheck

    def ishighlinkdensity(self, node):
        """check if a node contains lots of links"""
        text = util.getinnertext(node, True) 
        if not text:
            return False
        words = self.texthandler.splittext(text)
        linkbuffer = [] 
        for link in node.iterdescendants('a'):
            if link.text != None:
                linkbuffer.append(link.text)
        if len(linkbuffer) == 0:
            return False

        linktext = ' '.join(linkbuffer) 
        linkwords = self.texthandler.splittext(linktext)

        linkdivisor = len(linkwords)/len(words)
        score = linkdivisor * len(linkbuffer)
        
        logging.info("Link density score is %f for node %s"%(score, self._getshorttext(node)))
        return score > 1

    def _getshorttext(self,node):
        return etree.tostring(node).decode('utf-8')[:50]

    def isboostable (self, node ):
        """ make sure that the node is a paragraph, and connected to other paragraph """
        stepsaway = 0 
        minstopword = 5
        maxstepsaway = 3
        for sib in node.itersiblings(preceding=True):
            if(sib.tag == 'p'): 
                if stepsaway >= maxstepsaway:
                    logging.info("Next paragraph is too farway, not boost")
                    return False
                paratext = util.getinnertext(sib) 
                if paratext != None:
                    ws = self.texthandler.getstopwordscount(paratext)
                    if ws.stopwordcount > minstopword:
                        logging.info("Boosting this node")
                        return True
                stepsaway += 1

        return False

    def postextractionclean(self, topnode):
        """remove any divs that looks like non-content, link clusters"""
        node = self.addsiblings(topnode)
        for child in node.iterchildren():
            if child.tag == 'p':
                if self.ishighlinkdensity(child) or self.istablenopara(child) or isthresholdmet(child):
                    node.remove(child)
        return node

    def getbaselinescoreforsiblings(self, topnode):
        """get base score against average scoring of paragraphs within topnodes. Siblings must have higher score than baseline"""
        base = 100000
        numparas = 0
        scoreparas = 0 
        #nodestocheck = self.xparas(topnode)
        for node in topnode.iterdescendants('p'):
            nodetext = util.getinnertext(node)
            ws = self.texthandler.getstopwordscount(nodetext)
            linkdense = self.ishighlinkdensity(topnode)
            if(ws.stopwordcount > 2 and not linkdense):
                numparas += 1
                scoreparas += ws.stopwordcount

        if numparas > 0:
            base = scoreparas/ numparas
        return base

    def addsiblings(self, topnode):
        """ add content of siblings that are likely to be meaning ful to the topnode"""
        logging.debug("Start adding siblings")
        baselinescore = self.getbaselinescoreforsiblings(topnode)
        siblingcontent = []

        for sib in topnode.itersiblings(preceding=True):
            content = self.getsiblingcontent(sib, baselinescore)
            if content: 
                siblingcontent.append(content)

        for content in siblingcontent:
            paras = html.fragments_fromstring(content)
            for p in reversed(paras):
                self._insertFirst(topnode, p)

        return topnode

    def _insertFirst(self, parnode, node):
        childnodes = parnode.getchildren()
        if childnodes and len(childnodes) > 0:
            first = childnodes[0]
            first.addprevious(node)
        else:
            parnode.append(node)

        # preserve the relative order of text blks
        if parnode.text:
            node.tail = parnode.text
            parnode.text = None

    def getsiblingcontent(self, currentsibling, basescore):
        if currentsibling.tag == 'p' and len(util.getinnertext(currentsibling)) > 0:
            return util.getouterhtml(currentsibling)
        else:
            alltext = [] 
            for para in currentsibling.iterdescendants('p'):#self.xparas(currentsibling):
                text = util.getinnertext(para)
                if text and len(text) > 0 :
                    ws = self.texthandler.getstopwordscount(text)
                    parascore = ws.stopwordcount
                    if basescore * 0.30 < parascore:
                        alltext.append("<p>" + text + "</p>")

            if len(alltext) > 0:
                return " ".join(alltext)
            else:
                return None

    def istablenopara(self, node):
        for subpara in node.iterdescendants('p'):
            if len(util.getinnertext(subpara,True)) < 25:
                parent = subpara.getparent()
                if parent:
                    parent.remove(subpara)

        #subparas = self.xparas(node)
        iterpar = node.iterdescendants('p')
        try:
            p = next(iterpar)
            return False
        except StopIteration:
            if node.tag != 'td':
                return True
        
    def isthresholdmet(self, node):
        topnode = node.getparent()
        topnodescore = self._score(topnode)
        curscore = self._score(node)
        threshold = topnodescore * 0.08

        if curscore < threshold and node.tag != 'td':
            return False
        else:
            return True

        

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

