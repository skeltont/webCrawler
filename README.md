# webCrawler
simple script to take a specified URL, parse the retrieved HTML, and then
retrieve the HTML from all URLs found in `<a>` tags.

# Setup
From within the top level of the source directory, run
```
pip install -r requirements.txt
```

# Usage
## Basic Usage
```
/path/to/your/python3.8 crawler.py <URL>
```

## Advanced Usage
```
OPTIONS:
    --verbose:
        usage: `python3.8 crawler.py --verbose <URL>`
        default: False
        desc: print out additional logging information, like skipped href values
    --max_depth:
        usage: `python3.8 crawler.py --max_depth 3 <URL>`
        default: 2
        desc: how far links should be followed per link found.
    --max_threads:
        usage: `python3.8 crawler.py --max_threads 5 <URL>`
        default: 3
        desc: how many worker threads subscribed to the url queue to spin up.
```

all options can be used at the same time, i.e.
```
/path/to/your/python3.8 crawler.py --verbose --max_depth 3 --max_threads 3 <URL>
```