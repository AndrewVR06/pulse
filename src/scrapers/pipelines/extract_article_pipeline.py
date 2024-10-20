from sqlalchemy import text

from database import ExtractedArticleModel
from database.engine import DatabaseEngine
from scrapers.schemas.extract_article_input_schema import ExtractArticleInputSchema
from scrapers.schemas.summarise_article_input_schema import SummariseArticleInputSchema
from services.summary_service import SummaryService


class ExtractArticlePipeline:
    db_engine = DatabaseEngine()
    summary_service = SummaryService()

    async def process_item(self, item: ExtractArticleInputSchema, spider):

        async with self.db_engine.session_maker() as session:

            # Does this item already exist in the table?
            select_query = text("SELECT * FROM extracted_article WHERE article_id = :article_id")
            result = await session.execute(select_query, {"article_id": item.article_db_primary_key})
            article: ExtractedArticleModel = result.fetchone()
            if article:
                return SummariseArticleInputSchema(
                    **item.model_dump(), extracted_article_content=article.content, extracted_article_db_primary_key=article.id
                )

            extracted_article = await self.summary_service.isolate_article_text(item.content)

            query = text(f"INSERT INTO extracted_article (content, article_id) VALUES (:content, :article_id) RETURNING id")
            result = await session.execute(query, {"content": extracted_article, "article_id": item.article_db_primary_key})
            await session.commit()  # Need to commit all inserts/updates for them to take effect
            primary_key = result.scalar()

            return SummariseArticleInputSchema(
                **item.model_dump(), extracted_article_content=extracted_article, extracted_article_db_primary_key=primary_key
            )
