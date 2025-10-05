from fastapi import FastAPI

from rss_adapters.adapters.x import XAdapter, NitterRawAdapter


__version__ = "0.1"

app = FastAPI()


@app.get("/")
def healthcheck():
    return {
        "version": __version__
    }


@app.get("/x/{username}/feed.json")
def x_rss_feed(username: str):
    return XAdapter(username).fetch_feed().model_dump(exclude_none=True)



@app.get("/x/{username}/raw_feed.json")
def x_raw_rss_feed(username: str):
    return NitterRawAdapter(username).fetch_feed().model_dump()

