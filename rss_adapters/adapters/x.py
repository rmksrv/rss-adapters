import httpx
from dateutil.parser import parse as dateparse
from xmltodict import parse as xmlparse

from rss_adapters.adapters.proto import Adapter
from rss_adapters.schemas.proto import Feed, Item, Author, Attachment
from rss_adapters.schemas.nitter import NitterRss


USER_AGENT = r"FreshRSS/1.27.1 (Feed Parser; http://freshrss.org; Allow like Gecko) Build/1"

MAX_TITLE_LEN = 64
RSS_URL_TEMPL = r"https://nitter.privacyredirect.com/{username}/rss"


def _rss_url(username: str) -> str:
    return RSS_URL_TEMPL.format(username=username)


def _prettify_item_title(val: str) -> str:
    res = val
    if len(res) > MAX_TITLE_LEN:
        res = f"{res[:MAX_TITLE_LEN - 3]}..."
    res = res.replace("\n", " ")
    return res


class XAdapter(Adapter):

    def __init__(self, username: str) -> None:
        self.username = username

    def fetch_feed(self) -> Feed:
        resp = httpx.get(
            _rss_url(self.username), headers={"User-Agent": USER_AGENT}
        )
        rss = NitterRss.model_validate(xmlparse(resp.content).get("rss"))
        items = []
        for raw_item in rss.channel.item:
            title = _prettify_item_title(raw_item.title)
            date_published = dateparse(raw_item.pub_date)
            items.append(Item(
                id=raw_item.link,
                title=title,
                content_html=raw_item.description,
                summary=raw_item.title,
                image=None,  # TODO: lookup in content
                date_published=date_published,
                attachments=[],  # TODO: parse comments
            ))
        return Feed(
            version=rss.version,
            title=rss.channel.title,
            home_page_url=rss.channel.link,
            authors=[
                Author(
                    name=rss.channel.title, 
                    url=rss.channel.link, 
                    avatar=rss.channel.image.url,
                )
            ],
            language=rss.channel.language,
            items=items,
        )
