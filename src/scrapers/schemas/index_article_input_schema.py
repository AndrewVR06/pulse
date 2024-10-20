from scrapers.schemas.summarise_article_input_schema import SummariseArticleInputSchema


class IndexArticleInputSchema(SummariseArticleInputSchema):
    summarised_article_db_primary_key: int
    summarised_text: str
