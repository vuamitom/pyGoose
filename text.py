import regex
from structure import  Singleton
import logging
import util

class TextHandler(object):
    """docstring for StopWords"""
    def __init__(self):
        super(TextHandler, self).__init__()
        self.punctuation = regex.compile(r'[^\p{Ll}\p{Lu}\p{Lt}\p{Lo}\p{Nd}\p{Pc}\s]')
        self.spacesplit = regex.compile(r'\s+')
        #get stop words from file 
        self.swlist = StopWordSource.instance()
        self.tabnspaces = regex.compile(r"(\t|^\s+|\s+$|\s{2,})")
        self.linebreaks = regex.compile(r"\n")
        
    def removepunctuation(self,text):
        return self.punctuation.sub('',text)

    def removetabnspace(self,text):
        return self.tabnspaces.sub(' ',text)

    def widenlinebreak(self,text):
        return self.linebreaks.sub('',text)

    def splittext(self, text):
        return self.spacesplit.split(text)
        
    def getstopwordscount(self, content):
        ws = WordStat()
        if content is None:
            return ws
        strippedinput = self.removepunctuation(content) 
        candidate = self.splittext(strippedinput)
        swlist = StopWordSource.instance().getall()
        foundstpwords = []
        for c in candidate:
            if c.lower() in swlist:
                foundstpwords.append(c.lower())
        ws.wordcount = len(candidate)
        ws.stopwordcount = len(foundstpwords)
        ws.stopwords = foundstpwords
        #logging.info("found %d stopwords in text " % ws.stopwordcount )
        return ws

class WordStat(object):
    """status of a text"""
    def __init__(self):
        self.wordcount = 0
        self.stopwordcount = 0
        self.stopwords = None

@Singleton
class StopWordSource(object):
    """contain all stop words"""
    def __init__(self):
        self.infile = "stopwords-en.txt"
        self.swbuffer = None

    def getall(self):
        if self.swbuffer == None:
            self.swbuffer = []
            infile = open(self.infile)
            for l in infile:
                self.swbuffer.append(l.strip())
            logging.info("Source contains %d stop words " % len(self.swbuffer))
        return self.swbuffer

class Formatter(object):
    """ format resulting article text"""
    def __init__(self,config):
        self.texthandler = TextHandler()
        self.config = config

    def getformattedtext(self, topnode):
        """remove all unnecessary elements"""
        logging.debug("\nINITIAL \n" + util.getinnerhtml(topnode))
        self.remove_negscorenodes(topnode)
        logging.debug("After remove neg score nodes \n" + util.getinnerhtml(topnode))
        self.linkstotext(topnode)
        logging.debug("\nAfter linkstotext \n" + util.getinnerhtml(topnode))
        self.tagstotext(topnode)
        logging.debug("\nAfter tagstotext \n" + util.getinnerhtml(topnode))

        self.removetagswithfewwords(topnode)
        logging.debug("\nAfter remove fewword tags\n" + util.getinnerhtml(topnode))
        return self.totext(topnode)

    def remove_negscorenodes(self,topnode):
        scorednodes = topnode.cssselect("*[score]")
        for item in scorednodes:
            score = item.get('score')
            score = float(score) if score else 0
            if score < 1:
                item.getparent().remove(item)

    def linkstotext(self,topnode):
        """ clean and convert nodes that should be considered text"""
        for link in topnode.iterdescendants('a'):
            hasimg = link.iterdescendants('img')
            try:
                next(hasimg)
            except StopIteration:
                #replace with text
                util.replacewithtext(link)

    def tagstotext(self,topnode):
        """replace common non-blk with just text <b> <i> <strong>. Except <a> tag which is considered in linkstotext"""
        for tag in self.config.nonblktags:
            if tag != "a":
                for item in topnode.iterdescendants(tag):
                    util.replacewithtext(item)

    def removetagswithfewwords(self, topnode):
        """tags with fewer words than a threshold could be noise"""
        for item in topnode.iterdescendants():
            ws = self.texthandler.getstopwordscount(util.getinnertext(item, True))
            if ws.stopwordcount < 3 :
                try:
                    next(item.iterdescendants('object'))
                    next(item.iterdescendants('embed'))
                except StopIteration:
                    #remove node with there is no <object> <embed> tags
                    logging.debug("remove fewwordpara %s: %s "%(item.tag, item.text))
                    item.getparent().remove(item) 

    def totext(self,topnode):
        buff = []
        for child in topnode.iterchildren():
            content = util.getinnertext(child)
            if content:
                buff.append(content)

        if len(buff) > 0:
            return "\n\n".join(buff)
        else:
            return None


