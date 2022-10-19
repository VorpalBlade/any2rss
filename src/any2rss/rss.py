"""Generate an actual RSS feed from internal data structures."""

import datetime
from email.utils import format_datetime
from typing import Optional
import hashlib

import lxml.etree
from lxml.builder import ElementMaker

from . import _version
from .api import RSSItem, RSSFeed

_NSMAP = {"atom": "http://www.w3.org/2005/Atom"}

E = ElementMaker(nsmap=_NSMAP)
EAtom = ElementMaker(
    namespace="http://www.w3.org/2005/Atom",
    nsmap=_NSMAP,
)


def generate_entry(item: RSSItem):
    m = hashlib.sha256()
    m.update(item.link.encode("utf-8"))
    m.update(item.title.encode("utf-8"))
    m.update(item.description.encode("utf-8"))

    children = []
    if item.link:
        children.append(E("link", item.link))
    if item.published:
        formatted_date = format_datetime(item.published)
        children.append(E("pubDate", formatted_date))
        m.update(formatted_date.encode("utf-8"))
    return E(
        "item",
        E("title", item.title),
        E("description", item.description),
        E(
            "guid",
            m.hexdigest(),
            isPermaLink="false",
        ),
        *children,
    )


def generate_rss(feed: RSSFeed, url: str, pub_url: Optional[str] = None):
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
    if pub_url:
        children.append(
            EAtom("link", href=pub_url, rel="self", type="application/rss+xml")
        )
    channel = E(
        "channel",
        E("title", feed.title),
        E("lastBuildDate", format_datetime(datetime.datetime.utcnow())),
        E("ttl", "600"),
        E("generator", f"any2rss {_version.version}"),
        *children,
        *items,
    )
    rss = E(
        "rss",
        channel,
        version="2.0",
    )
    return lxml.etree.tostring(
        rss, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    ).strip()
