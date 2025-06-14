"""initial

Revision ID: 68dfe112f641
Revises: 
Create Date: 2024-10-20 12:46:12.242766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68dfe112f641'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('date_published', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('extracted_article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extracted_article_article_id'), 'extracted_article', ['article_id'], unique=True)
    op.create_table('summarised_article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pinecone_id', sa.String(length=64), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sentiment_score', sa.Integer(), nullable=False),
    sa.Column('vector_stored', sa.BOOLEAN(), nullable=True),
    sa.Column('extracted_article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['extracted_article_id'], ['extracted_article.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_summarised_article_extracted_article_id'), 'summarised_article', ['extracted_article_id'], unique=True)
    op.create_index(op.f('ix_summarised_article_pinecone_id'), 'summarised_article', ['pinecone_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_summarised_article_pinecone_id'), table_name='summarised_article')
    op.drop_index(op.f('ix_summarised_article_extracted_article_id'), table_name='summarised_article')
    op.drop_table('summarised_article')
    op.drop_index(op.f('ix_extracted_article_article_id'), table_name='extracted_article')
    op.drop_table('extracted_article')
    op.drop_table('article')
    # ### end Alembic commands ###
