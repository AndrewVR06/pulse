from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text

from ..base import Base


class ExtractedArticleModel(Base):
    __tablename__ = "extracted_article"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"), unique=True, index=True)
