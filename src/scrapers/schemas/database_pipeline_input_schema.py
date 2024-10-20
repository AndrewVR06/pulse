from pydantic import BaseModel, HttpUrl

from scrapers.schemas.crypto_panic_api_schema import ResultItem


class DatabasePipelineInputSchema(BaseModel):
    content: str
    source_url: HttpUrl
    cryptopanic_response: ResultItem
