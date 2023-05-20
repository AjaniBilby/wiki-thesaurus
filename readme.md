# Wiki Thesaurus

This CLI tool attempts to get similar words to any given input based on the graph structure of how Wikipedia pages are linked together.


## Installation

### Using pre-built

Clone this repository then extract the contents of [simplewiki.rar](https://github.com/AjaniBilby/wiki-thesaurus/releases/tag/v0.0.0) into the `./data/` folder.

### Building from source

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

Enter any text to perform a search, and start with a `.` to perform a command

| Command | Action
:-|:-
`.next` | Will show the next `x` results from the previous search
`.algo xxx` | Changes the search algorithm used, with the name corresponding to any algorithm in the folder `./algorithm/` (i.e. `.algo intersection` )
`.limit xxx` | Will change the number of results shown per search based on the number used in place of the `xxx` (i.e. `.limit 20`)
`.exit` | Ends the program