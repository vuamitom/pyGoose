class NotFoundException(Exception):
	"""docstring for NotFoundException"""
	def __init__(self, url):
		super(NotFoundException, self).__init__()
		self.url = url
		