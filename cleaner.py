"""
Clean ads, social network divs, comments
"""
import logging
logging.basicConfig(level=logging.INFO)

class DocumentCleaner(object):
    """docstring for DocumentCleaner"""
    def __init__(self):
        super(DocumentCleaner, self).__init__()
        

    def clean(self, article):
        logging.info("Cleaning article")
        doc = article.doc
        self.cleanem(doc)
        self.rm_scriptstyle(doc)


    def cleanem(self, doc):
        emlist = doc.findall(".//em")
        for node in emlist:
            images = node.findall(".//img")
            if(len(images) == 0):
                parent = node.getparent()
                parent.replace(node, node.text )

        logging.info(str(len(emlist)) + " EM tags modified")
        return doc
    
    def rm_dropcap(self, doc):
        """remove those css drop caps where they put the first letter in big text in the 1st paragraph"""

        
    def rm_scriptstyle(self, doc):
        style = doc.findall(".//style")
        for s in style: 
            parent = s.getparent()
            parent.remove(s)
        
        logging.info(str(len(style)) + " style tags removed")

        scripts = doc.findall(".//script")
        for s in scripts:
            parent = s.getparent()
            parent.remove(s)

        logging.info(str(len(scripts)) + " script tags removed ")

    def rm_para_spantags(self, doc):
        """When a span tag nests in a paragraph tag"""
        spans = doc.findall(".//p/span")
        for span in spans:
            paranode = span.getparent()
            paranode.replace(span, span.text)
            

