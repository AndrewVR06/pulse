from sqlalchemy import text

from database.engine import DatabaseEngine
from scrapers.schemas.database_pipeline_input_schema import DatabasePipelineInputSchema
from scrapers.schemas.extract_article_input_schema import ExtractArticleInputSchema


class DatabasePipeline:
    db_engine = DatabaseEngine()

    async def process_item(self, item: DatabasePipelineInputSchema, spider):

        async with self.db_engine.session_maker() as session:
            # Have we already put this item through the pipeline?
            query = text(f"SELECT * FROM article WHERE article.url = :url")
            result = await session.execute(query, {"url": str(item.source_url)})
            article = result.fetchone()

            if article:
                return ExtractArticleInputSchema(**item.model_dump(), article_db_primary_key=article.id)

            query = text("INSERT INTO article (url, content, date_published) VALUES (:url, :content, :date_published) RETURNING id")
            result = await session.execute(
                query, {"url": str(item.source_url), "content": item.content, "date_published": item.cryptopanic_response.published_at}
            )
            await session.commit()
            primary_key = result.scalar()

            return ExtractArticleInputSchema(**item.model_dump(), article_db_primary_key=primary_key)
