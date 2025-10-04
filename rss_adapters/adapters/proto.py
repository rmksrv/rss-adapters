import typing as t

from rss_adapters.schemas.proto import Feed


class Adapter(t.Protocol):
    def fetch_feed(self) -> Feed: ...

