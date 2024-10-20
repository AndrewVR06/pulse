from sqlalchemy import text

from database import SummarisedArticleModel
from database.engine import DatabaseEngine
from scrapers.schemas.index_article_input_schema import IndexArticleInputSchema
from scrapers.schemas.summarise_article_input_schema import SummariseArticleInputSchema
from services.summary_service import SummaryService


class SummariseArticlePipeline:
    db_engine = DatabaseEngine()
    summary_service = SummaryService()

    async def process_item(self, item: SummariseArticleInputSchema, spider):

        async with self.db_engine.session_maker() as session:

            # Does this item already exist in the table?
            select_query = text("SELECT * FROM summarised_article WHERE extracted_article_id = :extracted_article_id")
            result = await session.execute(select_query, {"extracted_article_id": item.extracted_article_db_primary_key})
            article: SummarisedArticleModel = result.fetchone()
            if article:
                return IndexArticleInputSchema(
                    **item.model_dump(), summarised_article_db_primary_key=article.id, summarised_text=article.content
                )

            summarised_article = await self.summary_service.summarise_crypto_news_artice(item.extracted_article_content)
            sentiment_score = self.summary_service.get_sentiment_score(summarised_article)

            query = text(
                f"INSERT INTO summarised_article (content, sentiment_score, extracted_article_id) VALUES (:content, :sentiment_score, :extracted_article_id) RETURNING id"
            )
            result = await session.execute(
                query,
                {
                    "content": summarised_article,
                    "sentiment_score": sentiment_score,
                    "extracted_article_id": item.extracted_article_db_primary_key,
                },
            )
            await session.commit()  # Need to commit all inserts/updates for them to take effect
            primary_key = result.scalar()

            # We only want to index articles that have some importance
            return IndexArticleInputSchema(
                **item.model_dump(), summarised_article_db_primary_key=primary_key, summarised_text=summarised_article
            )
