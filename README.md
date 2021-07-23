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
--verbose: print out additional logging information, like skipped href values.