'''module for scraping a web page at a supplied URL, finding all of the URLs on
that page so on.
'''

import re
import argparse
import threading
import queue
from collections import defaultdict
import requests

from bs4 import BeautifulSoup

class CrawlerURLError(Exception):
    '''custom exception class for when a supposed URL doesn't meet our
    validation criteria.
    '''

def validate_url(url):
    '''validate a URL's structure to have a leading http:// or https:// at a
    minimum.

    Params:
        url (str): the URL specified to navigate to.
    Raises:
        (CrawlerURLError): The url provided is of an invalid structure.
    '''

    if not isinstance(url, str):
        raise CrawlerURLError(f"{url} is of invalid type.")

    if not re.match(r'^(http|https)://', url):
        raise CrawlerURLError(f"{url} is of invalid format.")


class Crawler:
    '''crawler class for keeping track of important user-provided specifics
    on how to run the program and the data collected thus far.
    '''

    def __init__(self, max_threads=3, max_depth=2, verbose=False):
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.verbose = verbose

        self.urls = list()
        self.visited_pages = defaultdict(bool)

    def print_urls(self, parent_url, child_urls, ident=None):
        '''write the urls we've found in the neatest way possible

        Params:
            parent_url [str]: the URL specified to navigate to.
            child_urls ([str]): the URLs found on the page that was scraped.
            ident (str): the identifier of the thread
        '''

        str_fmt = f"{ident}: " if ident is not None and self.verbose else ""
        str_fmt = str_fmt + "{url}"

        print(str_fmt.format(url=parent_url))
        for url in child_urls:
            print("\t", str_fmt.format(url=url))


    def discover_urls(self, url):
        '''navigate to a specified page and collect all of the links found
        within

        Params:
            url (str): the URL specified to navigate to.
        Returns:
            links [(str)]: new URLs that we found on this particular page.
        '''

        # this is a broad catch, but a number of things can happen here and
        # I don't think I want to spend time narrowing them all down.
        try:
            resp = requests.get(url)
        except Exception as err: # pylint: disable=broad-except
            if self.verbose:
                print(f'failed to fetch {url}: {err}')
            return []

        # use beautifulsoup to parse the html
        soup = BeautifulSoup(resp.text, 'html.parser')

        # iterate over every <a> element found in the html response,
        # make sure we haven't seen it before and validate it's structure.
        links = list()
        for link in soup.find_all('a'):
            try:
                potential_link = link.get('href')
                if self.visited_pages[potential_link]:
                    continue

                validate_url(potential_link)
            except CrawlerURLError as err:
                continue

            # add to our list of urls to parse and keep track that we've seen
            # it so we maybe can avoid some loops.
            links.append(potential_link)
            self.visited_pages[potential_link] = True

        self.print_urls(url, links, threading.get_ident())

        return links

    def multithread_discover_urls(self, urls):
        '''manage multiple threads that are all parsing pages found at
        different URLs via a queue and continue to find them until there are
        no more threads.

        Params:
            urls ([str]): the URL specified to navigate to.
        '''

        # build a queue for all the urls that the threads can subscribe to
        # and determine when work is really done for that set of URLs.
        url_queue = queue.Queue()

        results = list()

        # worker function that describes each thread's job: pop a url off the
        # queue, discover new urls, and extend the result set shared by
        # all threads.
        def worker():
            while True:
                url = url_queue.get()
                results.extend(self.discover_urls(url))
                url_queue.task_done()

        # spin up a number of threads equal to user input or default max_threads
        for _ in range(self.max_threads):
            threading.Thread(target=worker, daemon=True).start()

        # while urls is populated or the max_depth hasn't been reached
        depth = 0
        while urls and depth < self.max_depth:
            # drain the list of urls into our queue
            while urls:
                url = urls.pop()
                url_queue.put((url))

            # wait for the threads we have running to finish their work and
            # extend the urls we are going to hit next.
            url_queue.join()

            urls.extend(results)

            # reset results and increment the depth
            results = []
            depth += 1


        # final reap in case there are still yet more URLs,
        # but we've reached max depth
        url_queue.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url', type=str, help='URL to navigate to and start scraping.')
    parser.add_argument('--verbose', default=False, action='store_true')
    parser.add_argument('--max_depth', type=int, default=2)
    parser.add_argument('--max_threads', type=int, default=10)

    args = parser.parse_args()

    crawler = Crawler(args.max_threads, args.max_depth, args.verbose)
    crawler.multithread_discover_urls([args.url])
