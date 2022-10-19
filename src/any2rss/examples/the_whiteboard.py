import datetime
import re

import bs4
from funcy import first

from any2rss.api import RSSFeed, RSSItem, HTML


def get_url(extra: dict[str, str]):
    """Return the URL to fetch, can be parameterized using extra arguments"""
    return "https://the-whiteboard.com/"


def get_parser(extra: dict[str, str]):
    """Should return which BeautifulSoup parser to use for this site.

    Valid options are (as of writing this):
    * html5lib (slow but lenient, extra dependency)
    * html.parser (medium speed, medium leniency, standard library)
    * lxml (quick, low leniency, any2rss already depends on this for RSS generation)
    """
    # This site is bad, doesn't work with lxml
    return "html5lib"


_RE_IMG = re.compile(r"^autotwb")


def extract(soup: bs4.BeautifulSoup, extra: dict[str, str]) -> RSSFeed:
    """Extract the elements for the feed from the page.

    :param soup: Soup object representing the page
    :param extra: Extra args as passed from command line by user.
    :return: An RSS feed object with what was found on the page.
    """
    # Locate image tags with a src value matching the regex
    img = soup.find("img", attrs={"src": _RE_IMG}, recursive=True)
    # The date is the first text child of the parent tag. Eww.
    date_str = first(img.parent.children)
    # Build an item for this
    item = RSSItem(
        title=f"The Whiteboard: {date_str}",
        description=HTML(img),
        # This is terrible, but on this website the archive page is not generated until the next day!
        link=get_url(extra),
        published=datetime.datetime.fromisoformat(date_str),
    )
    # Generate a feed. As we only have a single item (current page), this is OK.
    return RSSFeed(title="The Whiteboard", description=soup.title.text, items=[item])
