from urllib.parse import urljoin

import bleach
import bs4

from .api import HTML

_cleaner = bleach.sanitizer.Cleaner(
    tags=bleach.sanitizer.ALLOWED_TAGS
    + ["img", "div", "h1", "h2", "h3", "h4", "h5", "p", "br"],
    attributes=bleach.sanitizer.ALLOWED_ATTRIBUTES | {"img": ["src"]},
)


def fixup_tag(tag: bs4.Tag, name: str, attr: str, base_url: str):
    if tag.name == name and tag.has_attr(attr):
        tag[attr] = urljoin(base_url, tag[attr])
    for t in tag.find_all(name, **{attr: True}):
        t[attr] = urljoin(base_url, t[attr])


def make_absolute(tag: HTML, soup: bs4.BeautifulSoup, url: str):
    # Resolve URL
    base_url = tag.url_base
    if base_url is None:
        head = soup.find("head")
        if head:
            base = head.find("base")
            if base:
                base_url = base.attrs.get("href", None)
    if base_url is None:
        base_url = url
    # Process tags
    fixup_tag(tag.data, "a", "href", base_url)
    fixup_tag(tag.data, "img", "src", base_url)


def sanitize_html(tag: HTML):
    return _cleaner.clean(str(tag.data))


def clean_html(tag: HTML, soup: bs4.BeautifulSoup, url: str):
    make_absolute(tag, soup, url)
    return sanitize_html(tag)
