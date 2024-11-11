from pydantic import BaseModel


class QueryResult(BaseModel):
    id: str
    content: str
    date_published: int
