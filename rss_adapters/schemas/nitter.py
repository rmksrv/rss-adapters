import pydantic as pdc


class NitterItem(pdc.BaseModel):
    title: str
    description: str
    guid: str
    link: str
    pub_date: str = pdc.Field(alias="pubDate")
    dc_creator: str = pdc.Field(alias="dc:creator")


class NitterImage(pdc.BaseModel):
    title: str
    link: str
    url: str
    width: str
    height: str


class AtomLink(pdc.BaseModel):
    href: str = pdc.Field(alias="@href")
    rel: str = pdc.Field(alias="@rel")
    type: str = pdc.Field(alias="@type")


class NitterChannel(pdc.BaseModel):
    title: str
    link: str
    description: str
    language: str
    ttl: str
    image: NitterImage
    item: list[NitterItem]
    atom_link: AtomLink = pdc.Field(alias="atom:link")


class NitterRss(pdc.BaseModel):
    channel: NitterChannel
    version: str = pdc.Field(alias="@version")
    xmlns_atom: str = pdc.Field(alias="@xmlns:atom")
    xmlns_dc: str = pdc.Field(alias="@xmlns:dc")

