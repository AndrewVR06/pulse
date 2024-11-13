import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text

from database.engine import DatabaseEngine
from scrapers.tasks import crawl_crypto_panic

from app_config import get_settings
from services.anthropic_service import AnthropicService
from services.vector_service import VectorService

settings = get_settings()


app = FastAPI()


class Question(BaseModel):
    question: str
    days_ago: int


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.post("/question/", response_model=dict[str, str])
async def post_question(question: Question):
    v = VectorService()
    s = AnthropicService()

    time_cutoff = datetime.datetime.now() - datetime.timedelta(days=question.days_ago)
    top_results = await v.retrieve_top_k_results(question.question, time_cutoff, k=64)
    reranked_results = await v.rerank_results(question.question, top_results)

    # answer = await s.answer_question(question.question, reranked_results)
    answer = await s.predict(reranked_results)

    return {"answer": answer}


@app.get("/test-db/", response_model=dict[str, str])
async def get_test_db():
    db_engine = DatabaseEngine()

    async with db_engine.session_maker() as session:
        query = text(f"SELECT * FROM article")
        await session.execute(query)

    return {"success": "success"}


@app.post("/trigger-crawl/", response_model=dict[str, str])
async def trigger_crawl():
    """
    Endpoint to trigger the crypto_panic spider crawl
    """
    task = crawl_crypto_panic.delay()
    return {"result": "task has started"}
