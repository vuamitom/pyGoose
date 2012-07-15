"""
Clean ads, social network divs, comments
"""
import logging
from lxml import etree
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

    def clean(self, article):
        logging.info("Cleaning article")
        doc = article.doc
        self.cleanem(doc)
        self.rm_scriptstyle(doc)
        self.rm_dropcaps(doc)
        self.rm_para_spantags(doc)
        self.clean_badtags(doc)

    def _replacewithtext(self, node):
        """replace an element with its text """
        parent = node.getparent()
        parent.remove(node)
        try:
            prevsib = next(node.itersiblings(preceding=True))
            prevsib.tail = node.text
        except StopIteration:
            parent.text = node.text

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


    def rm_dropcaps(self, doc):
        """remove those css drop caps where they put the first letter in big text in the 1st paragraph"""
        items = self.xdropcap(doc)
        for item in items:
            #replace 
            self._replacewithtext(item)

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


