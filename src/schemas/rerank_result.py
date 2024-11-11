from pydantic import BaseModel


class RerankResult(BaseModel):
    index: int
    content: str
