# Wiki Thesaurus

This CLI tool attempts to get similar words to any given input based on the graph structure of how Wikipedia pages are linked together.


## Installation

Downloads and depacks the dataset of all english wikipedia articles
```
python download.py
```

Generate the article graph as a database
```
python ingest.py
```

## Use

Start-up
```
python search.py
```

Simply enter in any word you want results for, after which you can enter `.more` for more results from that query, or enter a new query.