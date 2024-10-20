from scrapers.schemas.database_pipeline_input_schema import DatabasePipelineInputSchema


class ExtractArticleInputSchema(DatabasePipelineInputSchema):
    article_db_primary_key: int
