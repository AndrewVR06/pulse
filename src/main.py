from fastapi import FastAPI, BackgroundTasks, HTTPException
import logging
from scrapers.crawler_runner import CrawlerRunner

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/trigger-crawl/", response_model=dict[str, str])
async def trigger_crawl(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger the crypto_panic spider crawl
    """
    try:
        # Run the spider in the background
        background_tasks.add_task(CrawlerRunner().run_spider)
        return {"status": "accepted", "message": "Crawl started in background"}
    except Exception as e:
        logging.error(f"Failed to start crawl: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
