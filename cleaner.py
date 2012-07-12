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
        

    def clean(self, article):
        logging.info("Cleaning article")
        doc = article.doc
        self.cleanem(doc)
        self.rm_scriptstyle(doc)

    def _replacewithtext(self, node):
        """replace an element with its text """
        parent = node.getparent()
        parent.remove(node)
        try:
            prevsib = next(node.itersiblings(Preceding=True))
            prevsib.tail = node.text
        except StopIteration:
            parent.text = node.text

    def cleanem(self, doc):
        emlist = self.xem(doc)
        for node in emlist:
            images = self.ximg(node) 
            if(len(images) == 0):
                self.replacewithtext(node)

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
            paranode = span.getparent()
            #replace span with text 


    def rm_dropcaps(self, doc):
        """remove those css drop caps where they put the first letter in big text in the 1st paragraph"""
        items = self.xdropcap(doc)
        for item in items:
            #replace 
            self.replacewithtext(item)

    def clean_badtags(self, doc):
        
            

