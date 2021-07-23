'''test module for crawler.py'''

import unittest
from crawler import Crawler, CrawlerURLError, validate_url

class TestClassInstantiation(unittest.TestCase):

    def test_attributes_succeeds(self):
        '''verify that the key attributes are set after instantiation'''

        crawler = Crawler(max_threads=4, max_depth=3, verbose=True)

        self.assertEqual(crawler.max_threads, 4)
        self.assertEqual(crawler.max_depth, 3)
        self.assertTrue(crawler.verbose)


class TestWebCrawlingDiscover(unittest.TestCase):

    def test_discover_urls_succeeds(self):
        crawler = Crawler(max_threads=4, max_depth=3, verbose=True)
        urls = crawler.discover_urls('http://automationpractice.com/index.php')

        self.assertIsInstance(urls, list)
        self.assertTrue(urls)

    def test_discover_urls_fails(self):
        crawler = Crawler(max_threads=4, max_depth=3, verbose=True)
        urls = crawler.discover_urls('http://notarealsite')

        self.assertIsInstance(urls, list)
        self.assertFalse(urls)


class TestURLValidation(unittest.TestCase):

    def test_validate_url_succeeds(self):
        try:
            validate_url('http://automationpractice.com/index.php')
        except CrawlerURLError:
            self.fail('validate_url() raised CrawlerURLError')

    def test_validate_url_fails(self):
        self.assertRaises(CrawlerURLError, validate_url, 'notarealsite')
        self.assertRaises(CrawlerURLError, validate_url, 123)


class TestWebCrawlingMultithreadedTerminates(unittest.TestCase):

    def test_multithreaded_discover_urls_terminates(self):
        crawler = Crawler(max_threads=4, max_depth=2, verbose=True)
        crawler.multithread_discover_urls(
            ['http://automationpractice.com/index.php'])


if __name__ == '__main__':
    unittest.main()
