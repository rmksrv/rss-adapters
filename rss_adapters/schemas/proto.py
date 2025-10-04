import typing as t
from datetime import datetime

import pydantic as pdc


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
