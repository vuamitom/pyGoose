import logging
class DocumentCleaner(object):
	"""docstring for DocumentCleaner"""
	def __init__(self):
		super(DocumentCleaner, self).__init__()
		

	def clean(self, article):
		logging.info("Cleaning article")
		doc = article.doc


	def cleanem(doc):
		emlist = doc.getElementsByTagName("em")
		for i in range(0, emlist.length):
			node = emlist.item(i)
			images = node.getElementsByTagName("img")
			if(images.length == 0):
				parent = node.parentNode
				parent.replaceChild(doc.createTextNode(node.nodeValue), node)

		logging.info(str(emlist.length) + " EM tags modified")
		return doc

		
		