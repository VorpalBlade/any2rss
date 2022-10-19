# any2rss: Create RSS feeds from broken websites

This programs scrapes HTML and outputs RSS. This is made to work on very,
very broken websites. Unlike projects such as [html2rss] which you should
use instead if that works for you.

Unlike other approaches that limit you by using a simplified DSL to
describe how to extract the data, this package gives you the full freedom
of Python. Any2rss manages downloading, caching, and parsing, handing of
to your code for the extraction. Then any2rss handles sanitising the HTML
and generation of the actual RSS document.

## Documentation

This project is in very early stages, there is almost no documentation. But
here is how to run the [example](src/any2rss/examples/the_whiteboard.py):

```console
$ # It is assumed you have set up venv and installed this package using pip.
$ any2rss -m any2rss.examples.the_whiteboard
<?xml version='1.0' encoding='UTF-8'?>
<rss version="2.0">
[...]
$
```

The idea is that you would use a cronjob to run any2rss to generate feeds
on your self-hosted web server, that you can then poll using your RSS
reader of choice.

[html2rss]: https://github.com/html2rss/html2rss