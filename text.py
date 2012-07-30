import re
from structure import  Singleton
class TextHandler(object):
    """docstring for StopWords"""
    def __init__(self):
        super(TextHandler, self).__init__()
        self.punctuation = re.compile(r'[^\p{Ll}\p{Lu}\p{Lt}\p{Lo}\p{Nd}\p{Pc}\s]')
        self.spacesplit = re.compile(r'\s+')
        #get stop words from file 
        self.swlist = StopWordSource.instance()
        self.tabnspaces = re.compile(r"(\t|^\s+$)")
        self.linebreaks = re.compile(r"\n")
        
    def removepunctuation(self,text):
        return self.punctuation.sub('',text)

    def removetabnspace(self,text):
        return self.tabnspaces.sub('',text)

    def widenlinebreak(self,text):
        return self.linebreaks.sub(r'\n\n',text)

    def splittext(self, text):
        return self.spacesplit.split(text)
        
    def getstopwordscount(self, content):
        ws = WordStat()
        if not content:
            return ws
        strippedinput = self.removepunctuation(content) 
        candidate = self.splittext(strippedinput)

        foundstpwords = []
        for c in candidate:
            if c.lower() in self.stopwords:
                foundstpwords.append(c.lower())
        ws.wordcount = len(candidate)
        ws.stopwordcount = len(foundstpwords)
        ws.stopwords = foundstpwords

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
                self.swbuffer.append(l)
        return self.swbuffer

