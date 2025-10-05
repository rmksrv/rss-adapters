import typing as t

from rss_adapters.schemas.proto import Feed


class Adapter(t.Protocol):
    @property
    def favicon(self) -> str | None: ...
    def fetch_feed(self) -> Feed: ...

