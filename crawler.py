'''module for scraping a web page at a supplied URL, finding all of the URLs on
that page so on.
'''

import re
import argparse
import threading
import time
import requests

from bs4 import BeautifulSoup

VERBOSE = False

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

    if not re.match(r'^(http|https)://', url):
        raise CrawlerURLError(f"{url} is of invalid format.")


def scrape_page(url):
    '''navigate to a specified page and collect all of the links found within

    Params:
        url (str): the URL specified to navigate to.
    '''

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    links = list()
    for link in soup.find_all('a'):
        try:
            potential_link = link.get('href')
            validate_url(potential_link)
        except CrawlerURLError as e:
            if VERBOSE:
                print(e, '... skipping.')
            continue

        links.append(potential_link)

    return links



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url', type=str, help='URL to navigate to and start scraping.')
    parser.add_argument('--verbose', default=False, action='store_true')
    args = parser.parse_args()

    VERBOSE = args.verbose

    scrape_page(args.url)
