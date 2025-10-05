from fastapi import FastAPI

from rss_adapters.adapters.x import XAdapter


__version__ = "0.1"

app = FastAPI()


@app.get("/")
def healthcheck():
    return {
        "version": __version__
    }


@app.get("/x/{username}")
def x_rss_feed(username: str):
    return XAdapter(username).fetch_feed()

