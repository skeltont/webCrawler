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

# globals for now, going to be converting this to a class.
MAX_THREADS = 3
VERBOSE = False
VISITED_PAGES = defaultdict(bool)

class CrawlerURLError(Exception):
    '''custom exception class for when a supposed URL doesn't meet our
    validation criteria.'''


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


def print_urls(urls, depth=0, ident=None):
    '''write the urls we've found in the neatest way possible

    Params:
        urls ([str]): the URL specified to navigate to.
    '''

    for url in urls:
        if VERBOSE:
            # log the identifier of the thread to prove that multiple threads
            # are doing work.
            print("\t"*depth, ident, url)
            continue

        print("\t"*depth, url)


def discover_urls(url):
    '''navigate to a specified page and collect all of the links found within

    Params:
        url (str): the URL specified to navigate to.
    '''

    # this is a broad catch, but a number of things can happen here and I don't
    # think I want to spend time narrowing them all down
    try:
        resp = requests.get(url)
    except Exception as err: # pylint: disable=broad-except
        if VERBOSE:
            print(f'failed to fetch {url}: {err}')
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    links = list()
    for link in soup.find_all('a'):
        try:
            potential_link = link.get('href')
            if VISITED_PAGES[potential_link]:
                continue

            validate_url(potential_link)
        except CrawlerURLError as err:
            if VERBOSE:
                print(err, '... skipping.')
            continue

        # add to our list of urls to parse and keep track that we've seen it
        # so we maybe can avoid some loops.
        links.append(potential_link)
        VISITED_PAGES[potential_link] = True

    return links


def multithread_discover_urls(urls):
    '''manage multiple threads that are all parsing pages found at different
    URLs via a queue and continue to find them until there are no more threads.

    Params:
        urls ([str]): the URL specified to navigate to.
    '''

    url_queue = queue.Queue()

    results = list()
    def worker():
        while True:
            (url, depth) = url_queue.get()
            results.extend(discover_urls(url))
            print_urls(results, depth, threading.get_ident())
            url_queue.task_done()

    for _ in range(MAX_THREADS):
        threading.Thread(target=worker, daemon=True).start()

    depth = 0
    while urls and depth < MAX_DEPTH:
        for _ in urls:
            url = urls.pop()
            url_queue.put((url, depth))

        # wait for the threads we have running to finish their work and
        # extend the urls we are going to hit next.
        url_queue.join()
        urls.extend(results)

        # reset results and increment the depth
        results = []
        depth += 1

    url_queue.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url', type=str, help='URL to navigate to and start scraping.')
    parser.add_argument('--verbose', default=False, action='store_true')
    parser.add_argument('--max_depth', type=int, default=2)
    parser.add_argument('--max_threads', type=int, default=10)

    args = parser.parse_args()

    VERBOSE = args.verbose
    MAX_THREADS = args.max_threads
    MAX_DEPTH = args.max_depth

    multithread_discover_urls([args.url])
