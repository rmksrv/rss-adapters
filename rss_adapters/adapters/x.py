import re
from urllib.parse import unquote

import httpx
from dateutil.parser import parse as dateparse
from xmltodict import parse as xmlparse

from rss_adapters.adapters.proto import Adapter
from rss_adapters.schemas.proto import Feed, Item, Author
from rss_adapters.schemas.nitter import NitterRss


USER_AGENT = r"FreshRSS/1.27.1 (Feed Parser; http://freshrss.org; Allow like Gecko) Build/1"

MAX_TITLE_LEN = 100
RSS_URL_TEMPL = r"https://nitter.privacyredirect.com/{username}/rss"
TWIMG_URL_TEMPL = r"https://pbs.twimg.com/media/{filename}"
IMG_SRC_RE = re.compile(
    r'(<img[^>]*?\bsrc\s*=\s*["\'])([^"\']+)(["\'])',
    flags=re.IGNORECASE
)


def _rss_url(username: str) -> str:
    return RSS_URL_TEMPL.format(username=username)


def _prettify_item_title(val: str) -> str:
    res = ". ".join(re.split(r"[.\n!?]", val)[:2])
    if len(res) > MAX_TITLE_LEN:
        res = f"{res[:MAX_TITLE_LEN - 3]}..."
    res = res.replace("\n", " ")
    return res


def _find_first_img_url(html: str) -> str | None:
    matched = re.search(r'<img( [a-zA-Z]+=.*)* src="(.*)"( [a-zA-Z]+=.*)*>', html)
    if not matched:
        return None
    return matched.group(2)


def _extract_username(url: str) -> str:
    matched = re.search(r"http[s]://(.*)/(.*)", url)
    if not matched:
        return ""
    return matched.group(2)


class NitterRawAdapter:

    def __init__(self, username: str) -> None:
        self.username = username

    def fetch_feed(self) -> NitterRss:
        resp = httpx.get(
            _rss_url(self.username), headers={"User-Agent": USER_AGENT}
        )
        rss = NitterRss.model_validate(xmlparse(resp.content).get("rss"))
        return rss


def _get_twimg_url(url: str) -> str:
    url = unquote(url)
    filename = url.rsplit("/", maxsplit=1)[-1]
    res = TWIMG_URL_TEMPL.format(filename=filename)
    return res


def _twimgify_images(html: str) -> str:

    def repl(match: re.Match) -> str:
        prefix, url, suffix = match.groups()
        try:
            new_url = _get_twimg_url(url)
        except Exception:
            new_url = url
        return f"{prefix}{new_url}{suffix}"

    return IMG_SRC_RE.sub(repl, html)


class XAdapter(Adapter):

    def __init__(self, username: str) -> None:
        self.username = username

    @property
    def favicon(self) -> str | None:
        return "https://x.com/favicon.ico"

    def fetch_feed(self) -> Feed:
        rss = NitterRawAdapter(self.username).fetch_feed()
        author_name = None
        if username := _extract_username(rss.channel.link):
            author_name = f"@{username}"
        authors = [Author(
            name=author_name, 
            url=rss.channel.link, 
            avatar=rss.channel.image.url,
        )]
        items = []
        for raw_item in rss.channel.item:
            title = _prettify_item_title(raw_item.title)
            image = None
            if img_in_content := _find_first_img_url(raw_item.description):
                image = _get_twimg_url(img_in_content)
            date_published = dateparse(raw_item.pub_date)
            item_authors = [*authors]
            if raw_item.dc_creator != author_name:
                item_authors.append(Author(name=raw_item.dc_creator))
            attachments = []
            items.append(Item(
                id=raw_item.link,
                url=raw_item.link,
                title=title,
                content_text=raw_item.title,
                content_html=_twimgify_images(raw_item.description),
                summary=raw_item.title,
                image=image,
                date_published=date_published,
                attachments=attachments,
                authors=item_authors,
            ))
        return Feed(
            title=rss.channel.title,
            favicon=self.favicon,
            home_page_url=rss.channel.link,
            authors=authors,
            language=rss.channel.language,
            items=items,
        )

