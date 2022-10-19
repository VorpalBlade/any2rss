"""
API for parsers to use. Everything else of any2rss is considered private.
"""

import dataclasses
import datetime

import bs4


@dataclasses.dataclass
class HTML:
    """Raw HTML, won't be escaped, but will be sanitised and URLs made absolute"""

    data: bs4.element.Tag
    # URL that things are relative to. By default, this will be figured out automatically
    url_base: str | None = None


@dataclasses.dataclass
class RSSItem:
    """An item in an RSS feed"""

    # Title of item, required
    title: str
    # Description of item, required. Typically, this contains data extracted from the page,
    # such the image from a web comic, or article text from a news site.
    description: str | HTML
    # Optional link to the source.
    link: str | None = None
    # Optional publish datetime.
    published: datetime.datetime | None = None


@dataclasses.dataclass
class RSSFeed:
    """An RSS feed. This is what parser modules should return"""

    # Title of the feed itself, required.
    title: str
    # List of items in the feed, required but can be empty.
    items: list[RSSItem]
    # Link to the feed, typically link to website.
    # Required in RSS, but will be defaulted to the site URL.
    link: str | None = None
    # Description of feed, required in RSS, will be defaulted to "No description".
    description: str | None = None
