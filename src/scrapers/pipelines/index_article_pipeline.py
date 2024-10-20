import hashlib
import logging

from sqlalchemy import text

from database import SummarisedArticleModel
from database.engine import DatabaseEngine
from schemas.document import Document
from scrapers.schemas.index_article_input_schema import IndexArticleInputSchema
from services.vector_service import VectorService


class IndexArticlePipeline:
    db_engine = DatabaseEngine()
    vector_service = VectorService()

    async def process_item(self, item: IndexArticleInputSchema, spider):

        if item is None:
            return

        async with self.db_engine.session_maker() as session:

            select_query = text("SELECT * FROM summarised_article WHERE id = :id")
            result = await session.execute(select_query, {"id": item.summarised_article_db_primary_key})
            article: SummarisedArticleModel = result.fetchone()
            if article.vector_stored is True or article.sentiment_score < 2:
                logging.info(f"Dropping article with url {item.source_url}")
                return

            hash_object = hashlib.sha256()
            hash_object.update(item.summarised_text.encode("utf-8"))
            hash_digest = hash_object.hexdigest()

            document = Document(
                text=item.summarised_text, url=str(item.source_url), hash=hash_digest, date_published=item.cryptopanic_response.published_at
            )
            await self.vector_service.store_document(document)

            query = text("UPDATE summarised_article SET pinecone_id = :pinecone_id, vector_stored = :vector_stored WHERE id = :id")
            await session.execute(query, {"pinecone_id": hash_digest, "vector_stored": True, "id": item.summarised_article_db_primary_key})
            await session.commit()
