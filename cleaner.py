"""
Clean ads, social network divs, comments
"""
import logging
import re
from lxml import etree
from text import TextHandler
logging.basicConfig(level=logging.INFO)

class DocumentCleaner(object):
    """docstring for DocumentCleaner"""
    def __init__(self):
        super(DocumentCleaner, self).__init__()
        #precompile xPath 
        self.xem = etree.XPath("//em")
        self.xstyle = etree.XPath("//style")
        self.ximg = etree.XPath("//img")
        self.xscript = etree.XPath("//script")
        self.xpara_span = etree.XPath("//p/span")
        self.xdropcap = etree.XPath("//span[contains(@class,'dropcap') or contains(@class,'drop-cap')]")
        #self.xdropcap = etree.XPath("//span[matches(@class,'(dropcap|drop-cap)')]")
        self.xwantedtags = etree.XPath("//*[self::div or self::span or self::article ]")
        self.xblkelemtags = etree.XPath("//*[self::a or self::blockquote or self::dl or self::div or self::img or self::ol or self::p or self::pre or self::table or self::ul]")
        #self.tabnspaces = re.compile(r"(\t|^\s+$)")
        #self.linebreaks = re.compile(r"\n")
        self.texthandler = TextHandler()


    def clean(self, article):
        logging.info("Cleaning article")
        doc = article.doc
        #logging.info(etree.tostring(doc,pretty_print=True))
        self.cleanem(doc)
        self.rm_scriptstyle(doc)
        self.rm_dropcaps(doc)
        self.rm_para_spantags(doc)
        self.clean_badtags(doc)
        self.tagstoparagraph(doc)
        logging.info(etree.tostring(doc, pretty_print=True).decode('utf-8'))


    def _replacewithtext(self, node):
        """replace an element with its text """
        parent = node.getparent()
        #parent.remove(node)
        nodetext = "%s %s" % ( node.text, node.tail )
        nodetext = nodetext.strip()
        logging.info("replace " + node.tag + " with text " + nodetext)

        try:
            prevsib = next(node.itersiblings(preceding=True))
            prevsib.tail = "%s %s" % (prevsib.tail, nodetext) 
            prevsib.tail = prevsib.tail.strip()
        except StopIteration:
            parent.text = ("%s %s" % ( parent.text, nodetext )).strip()

        parent.remove(node)

    def _replacewithpara(self, node):

        """replace an element with para <p> """
        parent = node.getparent()
        para = parent.makeelement('p')
        for child in node.iterchildren():
            para.append(child)
        parent.replace(node, para)

    def cleanem(self, doc):
        emlist = self.xem(doc)
        for node in emlist:
            images = self.ximg(node) 
            if(len(images) == 0):
                self._replacewithtext(node)

        logging.info(str(len(emlist)) + " EM tags modified")
        return doc
    
        
    def rm_scriptstyle(self, doc):
        """remove all <script> and <style> tags """
        style = self.xstyle(doc) 
        for s in self.xstyle(doc): 
            parent = s.getparent()
            parent.remove(s)
        
        logging.info(str(len(style)) + " style tags removed")

        scripts = self.xscript(doc) 
        for s in scripts:
            parent = s.getparent()
            parent.remove(s)

        logging.info(str(len(scripts)) + " script tags removed ")

    def rm_para_spantags(self, doc):
        """When a span tag nests in a paragraph tag"""
        spans = self.xpara_span(doc) 
        for span in spans:
            #replace span with text 
            self._replacewithtext(span)

        return doc


    def rm_dropcaps(self, doc):
        """remove those css drop caps where they put the first letter in big text in the 1st paragraph"""
        items = self.xdropcap(doc)
        for item in items:
            #replace 
            self._replacewithtext(item)
        return doc

    def clean_badtags(self, doc):
        """remove sidebar, block comments, reviews ... """
        noiselist = self.getnoisesource().getnoisyids()
        noisyIds = self.cssselect(doc, "id", noiselist)
        logging.info(str(len(noisyIds)) + " noisy ids removed ")
        for ele in noisyIds:
            ele.getparent().remove(ele)

        noisyclasses = self.cssselect(doc, "class", noiselist)
        logging.info(str(len(noisyclasses)) + " noisy classes removed ")
        for ele in noisyclasses: 
            ele.getparent().remove(ele)

        noisynames = self.cssselect(doc, "name", noiselist)
        logging.info(str(len(noisynames)) + " noisy names removed ")
        for ele in noisynames:
            ele.getparent().remove(ele)

        #clean bad tags that match regex
        pattern = self.getnoisesource().getnoisypatterns()
        noisypatterns = self.regexselect(doc, "id", pattern)
        logging.info(str(len(noisypatterns)) + " tag IDs match noisy patterns and removed ")
        for ele in noisypatterns:
            ele.getparent().remove(ele)

        noisypatterns = self.regexselect(doc, "class", pattern)
        logging.info(str(len(noisypatterns)) + " tag Classes match noisy patterns and removed ")
        for ele in noisypatterns:
            ele.getparent().remove(ele)
        return doc

    def tagstoparagraph(self, doc):
        """wrap orphan text in <p> tag. This situation is handled a bit different from Jim Goose
           It flushes the replacehtml buffer when <p> <article> or <div> is met"""
        for selectedtag in self.xwantedtags(doc):
            blkelems = self.xblkelemtags(selectedtag)
            if(len(blkelems) == 0):
                #replace element with para
                self._replacewithpara(doc,selectedtag) 
            else:
                #replace with a chosen tag
                self._getreplacement(doc,selectedtag)
        return doc

    def _getreplacement(self, doc, ele):
        replacehtml = None 
        if ele.text != None and ele.text.strip()!="":
            replacehtml = self._formattext(ele.text) 
            #remember to remove this text 
            ele.text = None

        for node in ele.iterchildren():
            if node.tag == 'a':
                replacehtml = ("%s %s" % (replacehtml,self._outerhtml(node))).strip()
                #remove node from document
                ele.remove(node)
            
            if node.tag == 'p' or node.tag == 'article' or node.tag == 'div':
                #wrap a <p> around the replacement buffer and insert
                if replacehtml != None:
                    newpara = self._createpara(ele, replacehtml)
                    node.addprevious(newpara)
                    replacehtml = None

            if node.tail != None and node.tail.strip()!="": 
                text = self._formattext(node.tail)
                replacehtml = ("%s %s" % (replacehtml , text)).strip()
                #remember to remove tail if necessary
                node.tail = None

        #flush all the text left
        if replacehtml != None:
            newpara = self._createpara(ele, replacehtml)
            ele.append(newpara)


    def _formattext(self, text):
        #result = re.sub(self.tabnspaces,"",text)
        #result = re.sub(self.linebreaks,r'\n\n',result)
        res = self.texthandler.removetabnspace(text)
        res = self.texthandler.widenlinebreak(res)
        return res

    def _createpara(self, parentele, innerhtml):
        para = etree.fromstring('<p>' + innerhtml + '</p>')
        para.base = parentele.base
        return para

    def _outerhtml(self, ele):
        return etree.tostring(ele).decode('utf-8')

    def regexselect(self, ele, attr, pattern):
        """clean tags that has attr matches a pattern"""
        regexpNS = "http://exslt.org/regular-expressions"
        path = etree.XPath("//*[re:test(@"+attr+",'" + pattern + "','i')]", namespaces={'re':regexpNS})
        return path(ele)

    def getnoisesource(self):
        return NoisyKeyProvider.instance()
    
    def cssselect(self, ele, attr, value):
        """wrapper around selecting DOM. using XPath. Can switch to cssselect incase of more specific need such as ^=, $=, ~="""
        terms = value.split("|")
        func = lambda t : "contains(@" + attr + ",'" + t + "')" 
        path = " or ".join(map(func, terms))
        path = "//*[" + path + "]" 
        filters = etree.XPath(path)
        return filters(ele)



from util import Singleton

@Singleton
class NoisyKeyProvider:
    """singleton class to provide list of noisy kewords""" 
    def __init__(self):
        self.noisykeywords = "side|combx|retweet|mediaarticlerelated|menucontainer|navbar|comment|PopularQuestions|\
        contact|foot|footer|Footer|footnote|cnn_strycaptiontxt|links|meta|scroll|shoutbox|sponsor\
        |tags|socialnetworking|socialNetworking|cnnStryHghLght|cnn_stryspcvbx|inset|pagetools|post-attributes|welcome_form|contentTools2|the_answers|remember-tool-tip\
        |communitypromo|runaroundLeft|subscribe|vcard|articleheadings|date|print|popup|author-dropdown|tools|socialtools|byline|konafilter|KonaFilter|breadcrumbs|fn|wp-caption-text"
        #self.noisypatterns = []
        #self.noisypatterns.append("[^-]facebook")
        #self.noisypatterns.append("^caption$")
        #self.noisypatterns.append("google")
        #self.noisypatterns.append("^entry-more.*$")
        #self.noisypatterns.append("[^-]twitter")
        #optimize regex
        self.noisypatterns = "^([^-]*(facebook|twitter)|(caption|entry-more.*)$)"

    def getnoisyids(self):
        return self.noisykeywords        

    def getnoisyclasses(self):
        return self.noisykeywords

    def getnoisypatterns(self):
        #return "(" + "|".join(self.noisypatterns) + ")"
        return self.noisypatterns


