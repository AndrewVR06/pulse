from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text, BOOLEAN, Integer

from ..base import Base


class SummarisedArticleModel(Base):
    __tablename__ = "summarised_article"

    id: Mapped[int] = mapped_column(primary_key=True)
    pinecone_id: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    sentiment_score: Mapped[int] = mapped_column(Integer, default=0)
    vector_stored: Mapped[bool] = mapped_column(BOOLEAN, default=False, nullable=True)

    extracted_article_id: Mapped[int] = mapped_column(ForeignKey("extracted_article.id"), unique=True, index=True)
