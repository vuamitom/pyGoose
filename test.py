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
        self.assertIsNotNone(article.title)
        self.assertIsNotNone(article.doc)
        self.assertIsNotNone(article.cleanedtext)
        logging.info("TITLE: " + article.title + "\n")
        logging.info(article.cleanedtext)

    def test_techcrunch(self):
        url = "http://techcrunch.com/2011/08/13/2005-zuckerberg-didnt-want-to-take-over-the-world/"
        article = self.tester.basic_extract(url)
        self._assertarticle(article)

    def test_cnn(self):
        url = "http://www.cnn.com/2010/POLITICS/08/13/democrats.social.security/index.html"
        article = self.tester.basic_extract(url)
        self._assertarticle(article)

    def test_vietnamnet(self):
        url = "http://vietnamnet.vn/vn/chinh-tri/83920/vn-va-my-khoi-dong-du-an-tay-doc-dioxin-lon-nhat.html"
        article = self.tester.basic_extract(url)
        self._assertarticle(article)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PopularSiteTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
