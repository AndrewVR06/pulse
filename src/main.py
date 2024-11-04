from fastapi import FastAPI
from scrapers.tasks import crawl_crypto_panic

from app_config import get_settings


settings = get_settings()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.post("/trigger-crawl/", response_model=dict[str, str])
async def trigger_crawl():
    """
    Endpoint to trigger the crypto_panic spider crawl
    """
    task = crawl_crypto_panic.delay()
    return {"result": "task has started"}
