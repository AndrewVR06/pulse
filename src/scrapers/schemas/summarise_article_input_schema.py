from scrapers.schemas.extract_article_input_schema import ExtractArticleInputSchema


class SummariseArticleInputSchema(ExtractArticleInputSchema):
    extracted_article_db_primary_key: int
    extracted_article_content: str
