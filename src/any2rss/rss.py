"""Generate an actual RSS feed from """
import datetime
from email.utils import format_datetime

import lxml.etree
from lxml.builder import E

from . import _version
from .api import RSSItem, RSSFeed


def generate_entry(item: RSSItem):
    children = []
    if item.link:
        children.append(E("link", item.link))
    if item.published:
        children.append(E("pubDate", format_datetime(item.published)))
    return E(
        "item",
        E("title", item.title),
        E("description", item.description),
        E(
            "guid",
            hex(
                hash(item.description)
                ^ hash(item.link)
                ^ hash(item.title)
                ^ hash(item.published)
            ),
            isPermaLink="false",
        ),
        *children,
    )


def generate_rss(feed: RSSFeed, url: str):
    children = []
    items = [generate_entry(e) for e in feed.items]
    if feed.description:
        children.append(E("description", feed.description))
    else:
        children.append(E("description", "No description"))
    if feed.link:
        children.append(E("link", feed.link))
    else:
        children.append(E("link", url))
    channel = E(
        "channel",
        E("title", feed.title),
        E("lastBuildDate", format_datetime(datetime.datetime.utcnow())),
        E("ttl", "600"),
        E("generator", f"any2rss {_version.version}"),
        *children,
        *items,
    )
    rss = E("rss", channel, version="2.0")
    return lxml.etree.tostring(
        rss, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    ).strip()
