from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List


class ResultItem(BaseModel):
    domain: str
    published_at: datetime
    url: HttpUrl


class CryptoPanicApiResponse(BaseModel):
    results: List[ResultItem]
