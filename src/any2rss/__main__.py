"""Main entry point"""

import argparse
import importlib
import importlib.util
from pathlib import Path

import appdirs
import bs4
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

from . import _version
from .api import RSSFeed, HTML
from .html_cleanup import clean_html
from .rss import generate_rss


def main():
    parser = argparse.ArgumentParser(
        prog="any2rss", description="Tool to extract rss feed from terrible sites"
    )
    parser.add_argument("--version", action="version", version=_version.version)
    parser.add_argument(
        "--from-file",
        type=Path,
        help="Load from file instead of URL, useful to avoid excessive HTTP requests during development",
    )
    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Print debug output (will make output invalid XML)",
    )
    def_file = parser.add_mutually_exclusive_group(required=True)
    def_file.add_argument("-f", "--file", type=Path, help="Path to definition file")
    def_file.add_argument("-m", "--module", type=str, help="Module name for definition")
    parser.add_argument(
        "extra",
        nargs="*",
        help="Extra arguments to the parser module on the form key=value",
    )

    args = parser.parse_args()
    extra = dict(e.split("=") for e in args.extra)

    # Load the module
    if args.file:
        spec = importlib.util.spec_from_file_location(args.file.name, args.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    elif args.module:
        mod = importlib.import_module(args.module)
    else:
        raise Exception("Impossible?")

    # Load the URL
    url = mod.get_url(extra=extra)

    cache_path = Path(appdirs.user_cache_dir("any2rss", "Vorpal")) / "web_cache"
    cache_path.mkdir(parents=True, exist_ok=True)
    sess = CacheControl(requests.Session(), cache=FileCache(str(cache_path)))

    if args.from_file:
        with args.from_file.open(mode="rb") as f:
            content = f.read()
    else:
        response = sess.get(url)
        # response = requests.get(url)
        content = response.content

    # Parse the HTML code
    parser = "html.parser"
    if hasattr(mod, "get_parser"):
        parser = mod.get_parser(extra=extra)

    soup = bs4.BeautifulSoup(content, parser)

    # Extract the feed using user provided module
    feed: RSSFeed = mod.extract(soup, extra=extra)

    # Clean up HTML
    clean_feed(feed, soup, url)
    if args.debug:
        print(feed)

    # Generate RSS
    print(generate_rss(feed, url).decode("utf-8"))


def clean_feed(feed: RSSFeed, soup: bs4.BeautifulSoup, url: str):
    for item in feed.items:
        if isinstance(item.description, HTML):
            item.description = clean_html(item.description, soup, url)


if __name__ == "__main__":
    main()
