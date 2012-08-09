# unit test
# for popular sites

import unittest
import logging
import util
from crawler import CrawlCandidate, Crawler

logging.basicConfig(level=logging.INFO)
class TestUtil(object):

    def basic_extract(self,url):
        config = util.Configuration()
        crawlcandidate = CrawlCandidate(config, url)
        crawler = Crawler(config)
        article = crawler.crawl(crawlcandidate)
        return article


class PopularSiteTest(unittest.TestCase):

    def setUp(self):
        logging.info("\nSetting up unit test ....")
        self.tester = TestUtil()

    def _assertarticle(self, article):
        self.assertIsNotNone(article.doc)
        self.assertIsNotNone(article.cleanedtext)
        logging.info(article.cleanedtext)

    def test_cnn(self):
        url = "http://techcrunch.com/2011/08/13/2005-zuckerberg-didnt-want-to-take-over-the-world/"
        article = self.tester.basic_extract(url)
        self._assertarticle(article)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PopularSiteTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
