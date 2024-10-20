import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text, Date

from ..base import Base


class ArticleModel(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    date_published: Mapped[datetime.date] = mapped_column(Date)
