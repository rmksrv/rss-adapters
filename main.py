import typing as t
from datetime import datetime
from xmltodict import parse as xmlparse

import httpx
import pydantic as pdc
from dateutil.parser import parse as dateparse
from fastapi import FastAPI


__version__ = "0.1"

app = FastAPI()


USER_AGENT = r"FreshRSS/1.27.1 (Feed Parser; http://freshrss.org; Allow like Gecko) Build/1"

X_RSS_URL_TEMPL = r"https://nitter.privacyredirect.com/{username}/rss"
X_MAX_TITLE_LEN = 64


@app.get("/")
def healthcheck():
    return {
        "version": __version__
    }


class Author(pdc.BaseModel):
    name: str | None = None
    url: str | None = None
    avatar: str | None = None

    @pdc.model_validator(mode="after")
    def verify_at_least_one_present(self) -> t.Self:
        if not self.name and not self.url and not self.avatar:
            raise ValueError("Author object should have at least one field set")
        return self


class Attachment(pdc.BaseModel):
    url: str
    mime_type: str
    title: str | None = None
    size_in_bytes: int | None = None
    duration_in_seconds: int | None = None


class Item(pdc.BaseModel):
    id: str
    title: str | None = None
    content_text: str | None = None
    content_html: str | None = None
    summary: str | None = None
    image: str | None = None
    banner_image: str | None = None
    url: str | None = None
    external_url: str | None = None
    date_published: datetime | None = None
    date_modified: datetime | None = None
    language: str | None = None
    authors: list[Author] = pdc.Field(default_factory=list)
    tags: list[str] = pdc.Field(default_factory=list)
    attachments: list[Attachment] = pdc.Field(default_factory=list)

    @pdc.model_validator(mode="after")
    def verify_content_present(self) -> t.Self:
        if not self.content_text and not self.content_html:
            raise ValueError("Neither `content_text` nor `content_html` are present")
        return self


class Feed(pdc.BaseModel):
    version: str
    title: str
    expired: bool = False
    home_page_url: str | None = None
    authors: list[Author] = pdc.Field(default_factory=list)
    language: str | None = None
    items: list[Item] = pdc.Field(default_factory=list)


@app.get("/x/{username}")
def x_rss_feed(username: str):
    url = X_RSS_URL_TEMPL.format(username=username)
    resp = httpx.get(url, headers={"User-Agent": USER_AGENT})
    base_rss = xmlparse(resp.content).get("rss", {})
    rss_ver = base_rss.get("@version")
    channel = base_rss.get("channel")
    feed_title = channel.get("title")
    link = channel.get("link")
    profile_pic = channel.get("image", {}).get("url")
    language = channel.get("language")
    # root = ET.fromstring(resp.content)
    # for item in root.findall("*item"):
    #     link = item.find("link")
    #     if link is None or not link.text:
    #         continue
    #     resp = httpx.get(link.text)
    #     = item.find("link")
    #
    # titles = root.findall("*item/title")
    # for title in titles:
    #     res_title = title.text or ""
    #     if res_title.startswith("R to"):
    #         res_title.replace("R to", "-> ", 1)
    #     if len(res_title) > X_MAX_TITLE_LEN:
    #         res_title = res_title[:X_MAX_TITLE_LEN - 3] + "..."
    #     res_title = re.split(".\n", res_title, maxsplit=1)[0]
    #     title.text = res_title
    # return JSONResponse(base_rss, 200)
    authors = [Author(name=feed_title, url=link, avatar=profile_pic)]
    items = []
    raw_items = channel.get("item", [])
    for item in raw_items:
        it_id = it_url = item.get("link")
        it_title = it_summary = item.get("title")
        if len(it_title) > X_MAX_TITLE_LEN:
            it_title = it_title[:X_MAX_TITLE_LEN - 3] + "..."
        it_title = it_title.replace("\n", " ")
        it_content = item.get("description")
        it_image = None  # TODO: lookup in content for image
        it_pub_date = dateparse(item.get("pubDate"))
        it_attachments = []  # TODO: lookup and parse comments
        items.append(Item(
            id=it_id,
            title=it_title,
            content_html=it_content,
            summary=it_summary,
            image=it_image,
            url=it_url,
            date_published=it_pub_date,
            attachments=it_attachments,
        ))

    return Feed(
        version=rss_ver,
        title=feed_title,
        home_page_url=link,
        authors=authors,
        language=language,
        items=items,
    )


