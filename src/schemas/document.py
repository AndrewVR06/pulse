import datetime

from pydantic import BaseModel


class Document(BaseModel):

    text: str
    url: str
    hash: str
    date_published: datetime.datetime
