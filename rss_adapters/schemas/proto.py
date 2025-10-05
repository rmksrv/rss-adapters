import typing as t
from datetime import datetime, timezone

import pydantic as pdc


def format_datetime(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat(timespec="seconds")


class BaseModel(pdc.BaseModel): ...


class Author(BaseModel):
    name: str | None = None
    url: str | None = None
    avatar: str | None = None

    @pdc.model_validator(mode="after")
    def verify_at_least_one_present(self) -> t.Self:
        if not self.name and not self.url and not self.avatar:
            raise ValueError("Author object should have at least one field set")
        return self


class Attachment(BaseModel):
    url: str
    mime_type: str
    title: str | None = None
    size_in_bytes: int | None = None
    duration_in_seconds: int | None = None


class Item(BaseModel):
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

    @pdc.field_serializer("date_published", "date_modified", mode="plain", when_used="json")
    def dump_dates(self, val: datetime | None) -> str | None:
        if val is None:
            return None
        return format_datetime(val)


class Feed(BaseModel):
    version: str = "https://jsonfeed.org/version/1.1"
    title: str = ""
    expired: bool = False
    home_page_url: str | None = None
    authors: list[Author] = pdc.Field(default_factory=list)
    language: str | None = None
    items: list[Item] = pdc.Field(default_factory=list)
    favicon: str | None = None
